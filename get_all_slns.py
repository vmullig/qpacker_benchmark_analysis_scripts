# Given a directory with a bunch of D-Wave response files, convert the bitstrings
# to solution indices.  Write the lowest-energy solution to a separate file.

import sys, os

import numpy as np
from interaction_graph_import.load_ascii_packing_problem import load_problem_from_ascii_file

################################################################################
# Functions:
################################################################################

def get_toulbar2_solution( filename ) :
    with open( filename ) as filehandle:
        lines = filehandle.readlines()

    outstring = "["
    seqpos_found = False
    time_found = False
    for line in lines:
        linestripped = line.strip()
        if linestripped.startswith("SEQPOS_") :
            linesplit = linestripped.split(" ")
            for entry in linesplit :
                onetwo = entry.split("=")
                seqpos = int(onetwo[0].split("_")[1])
                rotindex = int(onetwo[1].split("_")[1])
                if( outstring != "[" ) :
                    outstring += ","
                outstring += "(" + str(seqpos) + "," + str(rotindex) + ")"
            seqpos_found = True
            if time_found :
                break
        elif linestripped.startswith( "Optimum:" ) :
            linesplit = linestripped.split(" ")
            for i in range (1, len(linesplit) ) :
                if linesplit[i].startswith("microseconds") :
                    toulbar2_time = float( linesplit[i-1] )
                    break
            time_found = True
            if seqpos_found :
                break
    
    assert outstring != "["
    outstring += "]"
    return outstring, toulbar2_time
    

def calculate_rosetta_energy( rot_assignments, global_to_local_mappings, onebody_energies, twobody_energies_map ) :
    rotamers = []
    #print( global_to_local_mappings )
    for key in rot_assignments.keys() :
        val = rot_assignments[key]
        globalindex = -1
        for i in range(len(global_to_local_mappings)) :
            if global_to_local_mappings[i][0] == key and global_to_local_mappings[i][1] == val :
                globalindex = i
                break
        #print( key, val, globalindex )
        assert( globalindex != -1 )
        rotamers.append( globalindex )

    #print( "ROTAMERS\n", rotamers )
    
    onebody_sum = float(0.0)
    twobody_sum = float(0.0)
    for rotamer in rotamers:
        onebody_sum += onebody_energies[rotamer]

    # print( twobody_energies_map.keys() )

    for i in range( 1, len(rotamers) ) :
        for j in  range( 0, i ) :
            if (j,i) in twobody_energies_map :
                twobody_sum += twobody_energies_map[j,i]

    # print( "Onebody", onebody_sum )
    # print( "Twobody", twobody_sum )

    return onebody_sum + twobody_sum

def extract_total_time( filename ) :
    with open(filenamepath) as filehandle:
        filecontents = filehandle.read().split(",")
    #print( filecontents )
    timeval = None
    for entry in filecontents:
        if entry.find( "\"qpu_sampling_time\"" ) != -1 :
            splitentry = entry.split(" ")
            #print( splitentry )
            timeval = float(splitentry[len(splitentry) - 1])
            break
    assert timeval is not None, "Could not find \"qpu_sampling_time\" in file " + filename + "!"
    return timeval


################################################################################
# Actual execution starts here:
################################################################################

assert len(sys.argv) == 4, "Expected calling format: python3 get_all_slns.py <problem_file> <path_to_response_files> <toulbar2_file>"
problem_file = sys.argv[1]
solution_path = sys.argv[2]
toulbar2_file = sys.argv[3]
if solution_path[len(solution_path)-1] != "/" : solution_path = solution_path + "/"

# Read the problem definition:
nodeindex_to_nrotamers, global_to_local_mappings, onebody_energies, twobody_energies, aacomp_collection = load_problem_from_ascii_file( problem_file, format='default' )
twobody_energies_map = {}
for entry in twobody_energies :
    twobody_energies_map[int(entry[0]), int(entry[1])] = entry[2]

# Read the Toulbar2 solution:
toulbar2_solution, toulbar2_time = get_toulbar2_solution( toulbar2_file )

# Count rotamers:
total_rotamers = len( global_to_local_mappings )
print( global_to_local_mappings )
print("--------------------------------------------------------------------------------")
print(nodeindex_to_nrotamers)
print("--------------------------------------------------------------------------------")
print(onebody_energies)
print("--------------------------------------------------------------------------------")
print(twobody_energies_map)
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

# Finding lowest-energy solution
minE = None
best_solution = None

# Computing time
total_time_microseconds = 0.0

for filename in os.listdir(solution_path):
    filenamepath = os.path.join(solution_path, filename)
    # checking if it is a file
    if os.path.isfile(filenamepath) :
        if filenamepath.find( "_timing_" ) != -1 :
            total_time_microseconds += extract_total_time( filenamepath )
        elif filenamepath.find( "_response_" ) != -1 :
            filecounter += 1
            print( filenamepath )
            print( "Rotamer_selection\tComputer_energy\tRosetta_energy\tTimes_seen" )

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

                rosetta_energy = calculate_rosetta_energy( rot_assignments, global_to_local_mappings, onebody_energies, twobody_energies_map )

                if( minE == None or rosetta_energy < minE ) :
                    minE = rosetta_energy
                    best_solution = outstr

                outstr += " " + linesplit[len(linesplit) - 2] + " " + str(rosetta_energy) + " " + linesplit[len(linesplit) - 1].strip()
                print( outstr )
                valid_rot_count += nsamples

print( "Number of unique rotamer assignments: " + str(len(rotassignment_counts)) )
print( "Instances of multiple rotamers assigned: " + str(multi_rot_count) )
print( "Instances of no rotamers assigned: " + str(no_rot_count) )
print( "Valid samples: " + str(valid_rot_count))
assert( valid_rot_count + no_rot_count + multi_rot_count == samplecounter )
print( "Total samples: " + str(samplecounter) )
print( "Best solution:\t" + best_solution )
print( "Toulbar2 lowest-energy solution:\t" + toulbar2_solution )
print( "Toulbar2 time (us):\t" + str(toulbar2_time) )
if toulbar2_solution == best_solution :
    print(  "QPacker best is Toulbar2 lowest energy:\tTRUE" )
else :
    print(  "Best is lowest energy:\tFALSE" )
print( "Best solution Rosetta energy:\t" + str(minE) )
print( "Times best solution seen:\t" + str(rotassignment_counts[best_solution]) )
print( "Fraction of times best solution seen:\t" + str(rotassignment_counts[best_solution] / float(samplecounter)) )
print( "Total sampling time (us):\t" + str(total_time_microseconds) )
print( "Average time per sample (us):\t" + str(total_time_microseconds / float(samplecounter)) )
print( "Expectation time to find best solution (us):\t" + str(total_time_microseconds / float(rotassignment_counts[best_solution])) )
print( "Solution space size:\t", np.prod( nodeindex_to_nrotamers ) )