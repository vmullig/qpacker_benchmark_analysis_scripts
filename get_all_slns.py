# Given a directory with a bunch of D-Wave response files, convert the bitstrings
# to solution indices.  Write the lowest-energy solution to a separate file.

import sys, os
from interaction_graph_import.load_ascii_packing_problem import load_problem_from_ascii_file

assert len(sys.argv) == 4, "Expected calling format: python3 get_all_slns.py <problem_file> <path_to_response_files> <path_to_output_files>"
problem_file = sys.argv[1]
solution_path = sys.argv[2]
output_path = sys.argv[3]
if solution_path[len(solution_path)-1] != "/" : solution_path = solution_path + "/"
if output_path[len(output_path)-1] != "/" : output_path = output_path + "/"

# Read the problem definition:
nodeindex_to_nrotamers, global_to_local_mappings, onebody_energies, twobody_energies, aacomp_collection = load_problem_from_ascii_file( problem_file, format='default' )

# Count rotamers:
total_rotamers = len( global_to_local_mappings )
print( global_to_local_mappings )
print("--------------------------------------------------------------------------------")
print(nodeindex_to_nrotamers)
print("--------------------------------------------------------------------------------")

# Make a list of packable positions:
all_positions = []
for entry in global_to_local_mappings :
    if entry[0] not in all_positions :
        all_positions.append(entry[0])

filecounter = 0
samplecounter = 0

# Counters for unique and bad rotamer assignments
rotassignment_counts = {}
multi_rot_count = 0 #Number of cases with more than one rotamer assigned to a position.
no_rot_count = 0 #Number of cases with no rotamer assigned to a position.
valid_rot_count = 0 #Number of cases with a valid rotamer assignment.

for filename in os.listdir(solution_path):
    filenamepath = os.path.join(solution_path, filename)
    # checking if it is a file
    if os.path.isfile(filenamepath) and filenamepath.find( "_response_" ) != -1 :
        filecounter += 1
        print( filenamepath )

        # Parse the file:
        with open(filenamepath) as filehandle:
            filecontents = filehandle.readlines()
        firstline = True
        for line in filecontents:
            if(firstline == True) :
                firstline = False
                continue
            #print(line.strip())

            # Rotamer assignments map (map of seqpos->rotamer index)
            rot_assignments = {}

            # Parse the line:
            linesplit = line.split(",")
            assert len(linesplit) == total_rotamers + 3
            nsamples = int( linesplit[len(linesplit) - 1].strip() )
            samplecounter += nsamples
            #print(linesplit)
            nodeindex = -1
            old_seqpos = -1
            breaknow = False
            for i in range(0, total_rotamers) :
                seqpos = global_to_local_mappings[i][0]
                if seqpos != old_seqpos :
                    old_seqpos = seqpos
                    nodeindex += 1
                if int(linesplit[i]) == 1 or nodeindex_to_nrotamers[nodeindex] == 1 :
                    local_rotindex = global_to_local_mappings[i][1]
                    assert seqpos in all_positions
                    if seqpos in rot_assignments :
                        #print( "BAD -- Multiple rotamers assigned." )
                        multi_rot_count += nsamples
                        breaknow = True
                        break
                    rot_assignments[seqpos] = local_rotindex
            if( breaknow ) :
                continue

            # Sanity checks:
            if len(rot_assignments) != len(all_positions) :
                #print( "BAD -- No rotamer assigned at one or more positions." )
                no_rot_count += nsamples
                continue

            outstr = "["
            for i in range(len(all_positions)) :
                pos = all_positions[i]
                assert pos in rot_assignments, "Error! Seqpos " + str(pos) + " is not in rot_assignments " + str(rot_assignments)
                outstr += "(" + str(pos) + "," + str(rot_assignments[pos]) + ")"
                if( i < len(all_positions) - 1) :
                    outstr += ","
            outstr += "]"
            if outstr in rotassignment_counts :
                rotassignment_counts[outstr] += nsamples
            else :
                rotassignment_counts[outstr] = nsamples
            outstr += " " + linesplit[len(linesplit) - 2] + " " + linesplit[len(linesplit) - 1].strip()
            print( outstr )
            valid_rot_count += nsamples
        
print("Number of unique rotamer assignments: " + str(len(rotassignment_counts)) )
print("Instances of multiple rotamers assigned: " + str(multi_rot_count) )
print("Instances of no rotamers assigned: " + str(no_rot_count) )
print("Valid samples: " + str(valid_rot_count))
assert( valid_rot_count + no_rot_count + multi_rot_count == samplecounter )
print("Total samples: " + str(samplecounter) )
