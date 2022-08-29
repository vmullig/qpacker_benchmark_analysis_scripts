# Given a directory with a bunch of D-Wave response files, convert the bitstrings
# to solution indices.  Write the lowest-energy solution to a separate file.

import sys, os

import numpy as np
from interaction_graph_import.load_ascii_packing_problem import load_problem_from_ascii_file

################################################################################
# Functions:
################################################################################

def calculate_ref2015_energy( rot_assignments, global_to_local_mappings, onebody_energies, twobody_energies_map ) :
    rotamers = []
    #print( global_to_local_mappings )
    for key in rot_assignments :
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
        #print( "Adding onebody[" + str(rotamer) + "] " + str(onebody_energies[rotamer]) + "." )
        onebody_sum += onebody_energies[rotamer]

    # print( twobody_energies_map.keys() )

    for i in range( 1, len(rotamers) ) :
        for j in  range( 0, i ) :
            firstrot = rotamers[j]
            secondrot = rotamers[i]
            if (firstrot,secondrot) in twobody_energies_map :
                #print( "Adding twobody " + str(twobody_energies_map[firstrot,secondrot]) + "." )
                twobody_sum += twobody_energies_map[firstrot,secondrot]

    # print( "Onebody", onebody_sum )
    # print( "Twobody", twobody_sum )
    # print( "Total\t", onebody_sum + twobody_sum) 

    # exit()
    return onebody_sum + twobody_sum

## @brief Format a string of the format:
## 1:4,2:1,3:1,4:1,5:5,6:1,7:3,8:1,10:1
## to instead be:
## [(1,4),(2,1),(3,1),(4,1),(5,5),(6,1),(7,3),(8,1),(10,1)]
## @returns Formatted solution string, solution energy.
def format_rosetta_solution( soln_in, global_to_local_mappings, onebody_energies, twobody_energies_map ) :
    soln_out = "["
    rot_assignments = {}
    soln_in_separated = soln_in.split(",")
    assert len( soln_in_separated ) > 0
    for entry in soln_in_separated :
        entrypair = entry.split(":")
        assert len( entrypair ) == 2
        posn = int(entrypair[0])
        rotindex = int(entrypair[1])
        assert posn not in rot_assignments
        rot_assignments[posn] = rotindex
        if soln_out != "[" :
            soln_out += ","
        soln_out += "(" + str(posn) + "," + str(rotindex) + ")"
    soln_out += "]"
    soln_energy = calculate_ref2015_energy( rot_assignments, global_to_local_mappings, onebody_energies, twobody_energies_map )
    return soln_out, soln_energy

## @brief Read the Rosetta solutions.
def get_rosetta_solutions( filename, global_to_local_mappings, onebody_energies, twobody_energies_map ) :
    with open( filename ) as filehandle:
        lines = filehandle.readlines()

    solutions = []
    best_solution = None
    best_energy = None
    times = []
    rosetta_energies = []
    avgtime_us = None
    rotassignment_counts = {}

    in_solutions = False
    solutions_found = False
    
    for line in lines:
        if in_solutions == False :
            if solutions_found == False and line.startswith( "Time" ) :
                in_solutions = True
                continue
            elif solutions_found == True :
                if line.startswith("AverageTime:") :
                    splitline = line.split()
                    assert len( splitline ) == 2
                    avgtime_us = float( splitline[1] )
        
        if in_solutions == True :
            if line == ""  :
                in_solutions = False
                continue
            solutions_found = True
            splitline = line.split()
            assert len(splitline) == 3
            solnstring, energy = format_rosetta_solution( splitline[2], global_to_local_mappings, onebody_energies, twobody_energies_map )
            solutions.append( solnstring )
            times.append( float( splitline[0] ) )
            rosetta_energies.append(energy)
            if solnstring in rotassignment_counts :
                rotassignment_counts[solnstring] += 1
            else :
                rotassignment_counts[solnstring] = 1
            if best_solution == None or energy < best_energy :
                best_solution = solnstring
                best_energy = energy

        
    assert solutions_found == True
    assert avgtime_us != None
    assert best_solution != None
    assert best_energy != None

    return solutions, best_solution, best_energy, times, rosetta_energies, avgtime_us, rotassignment_counts


## @brief Read the Toulbar2 solution.
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
            optimal_energy = float( linesplit[1] )
            for i in range (1, len(linesplit) ) :
                if linesplit[i].startswith("microseconds") :
                    toulbar2_time = float( linesplit[i-1] )
                    break
            time_found = True
            if seqpos_found :
                break
    
    assert outstring != "["
    outstring += "]"
    return outstring, toulbar2_time, optimal_energy

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

assert len(sys.argv) == 5, "Expected calling format: python3 get_all_slns.py <problem_file> <path_to_response_files> <toulbar2_file> <rosetta_file>"
problem_file = sys.argv[1]
solution_path = sys.argv[2]
toulbar2_file = sys.argv[3]
rosetta_file = sys.argv[4]
if solution_path[len(solution_path)-1] != "/" : solution_path = solution_path + "/"

# Read the problem definition:
nodeindex_to_nrotamers, global_to_local_mappings, onebody_energies, twobody_energies, aacomp_collection = load_problem_from_ascii_file( problem_file, format='default' )
twobody_energies_map = {}
for entry in twobody_energies :
    twobody_energies_map[int(entry[0]), int(entry[1])] = entry[2]

# Read the Toulbar2 solution:
toulbar2_solution, toulbar2_time, toulbar2_energy = get_toulbar2_solution( toulbar2_file )

# Read the Rosetta solutions:
rosetta_solutions, best_rosetta_solution, best_rosetta_solution_energy, rosetta_times, rosetta_energies, rosetta_avg_time, rosetta_rotassignment_counts = get_rosetta_solutions( rosetta_file, global_to_local_mappings, onebody_energies, twobody_energies_map )

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
qpacker_samplecounter = 0

# Counters for unique and bad rotamer assignments
qpacker_rotassignment_counts = {}
qpacker_multi_rot_count = 0 #Number of cases with more than one rotamer assigned to a position.
qpacker_no_rot_count = 0 #Number of cases with no rotamer assigned to a position.
qpacker_valid_rot_count = 0 #Number of cases with a valid rotamer assignment.

# Finding lowest-energy solution
qpacker_minE = None
best_qpacker_solution = None

# Computing time
total_qpacker_time_microseconds = 0.0

for filename in os.listdir(solution_path):
    filenamepath = os.path.join(solution_path, filename)
    # checking if it is a file
    if os.path.isfile(filenamepath) :
        if filenamepath.find( "_timing_" ) != -1 :
            total_qpacker_time_microseconds += extract_total_time( filenamepath )
        elif filenamepath.find( "_response_" ) != -1 :
            filecounter += 1
            print( filenamepath )
            print( "Rotamer_selection\tDWave_Computer_energy\tQPacker_ref2015_energy\tTimes_seen" )

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
                qpacker_samplecounter += nsamples
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
                            qpacker_multi_rot_count += nsamples
                            breaknow = True
                            break
                        rot_assignments[seqpos] = local_rotindex
                if( breaknow ) :
                    continue

                # Sanity checks:
                if len(rot_assignments) != len(all_positions) :
                    #print( "BAD -- No rotamer assigned at one or more positions." )
                    qpacker_no_rot_count += nsamples
                    continue

                outstr = "["
                for i in range(len(all_positions)) :
                    pos = all_positions[i]
                    assert pos in rot_assignments, "Error! Seqpos " + str(pos) + " is not in rot_assignments " + str(rot_assignments)
                    outstr += "(" + str(pos) + "," + str(rot_assignments[pos]) + ")"
                    if( i < len(all_positions) - 1) :
                        outstr += ","
                outstr += "]"
                if outstr in qpacker_rotassignment_counts :
                    qpacker_rotassignment_counts[outstr] += nsamples
                else :
                    qpacker_rotassignment_counts[outstr] = nsamples

                qpacker_ref2015_energy = calculate_ref2015_energy( rot_assignments, global_to_local_mappings, onebody_energies, twobody_energies_map )

                if( qpacker_minE == None or qpacker_ref2015_energy < qpacker_minE ) :
                    qpacker_minE = qpacker_ref2015_energy
                    best_qpacker_solution = outstr

                outstr += " " + linesplit[len(linesplit) - 2] + " " + str(qpacker_ref2015_energy) + " " + linesplit[len(linesplit) - 1].strip()
                print( outstr )
                qpacker_valid_rot_count += nsamples

# QPacker analysis:
print( "Number of unique QPacker rotamer assignments: " + str(len(qpacker_rotassignment_counts)) )
print( "Instances of multiple QPacker rotamers assigned: " + str(qpacker_multi_rot_count) )
print( "Instances of no QPacker rotamers assigned: " + str(qpacker_no_rot_count) )
print( "Valid QPacker samples: " + str(qpacker_valid_rot_count))
assert( qpacker_valid_rot_count + qpacker_no_rot_count + qpacker_multi_rot_count == qpacker_samplecounter )
print( "Total QPacker samples: " + str(qpacker_samplecounter) )
print( "Best QPacker solution: " + best_qpacker_solution )
print( "Best QPacker solution ref2015 energy:\t" + str(qpacker_minE) )
print( "Times best QPacker solution seen:\t" + str(qpacker_rotassignment_counts[best_qpacker_solution]) )
print( "Fraction of times best QPacker solution seen:\t" + str(qpacker_rotassignment_counts[best_qpacker_solution] / float(qpacker_samplecounter)) )
print( "Total QPacker sampling time (us):\t" + str(total_qpacker_time_microseconds) )
print( "Average QPacker time per sample (us):\t" + str(total_qpacker_time_microseconds / float(qpacker_samplecounter)) )
print( "QPacker expectation time to find best solution (us):\t" + str(total_qpacker_time_microseconds / float(qpacker_rotassignment_counts[best_qpacker_solution])) )

# Rosetta analysis:
print( "Number of unique Rosetta rotamer assignments: " + str(len(rosetta_rotassignment_counts)) )
print( "Total Rosetta samples: " + str( len(rosetta_solutions ) ) )
print( "Best Rosetta solution: " + best_rosetta_solution )
print( "Best Rosetta solution ref2015 energy: " + best_rosetta_solution_energy )
print( "Times best Rosetta solution seen:\t" + str(rosetta_rotassignment_counts[best_rosetta_solution]) )
print( "Fraction of times best Rosetta solution seen:\t" + str(rosetta_rotassignment_counts[best_rosetta_solution] / float(len(rosetta_solutions))) )
print( "Total Rosetta sampling time (us):\t" + str( sum( rosetta_times ) ) )
print( "Average Rosetta time per sample (us):\t" + str( rosetta_avg_time ) )
print( "Rosetta expectation time to find best solution (us):\t" + str(sum( rosetta_times ) / float(rosetta_rotassignment_counts[best_rosetta_solution])) )

# Toulbar2 analysis:
print( "Toulbar2 lowest-energy solution:\t" + toulbar2_solution )
print( "Toulbar2 time (us):\t" + str(toulbar2_time) )
print( "Toulbar2 energy:\t" + str( toulbar2_energy ) )
if toulbar2_solution == best_qpacker_solution :
    print(  "QPacker best is Toulbar2 lowest energy:\tTRUE" )
else :
    print(  "QPacker best is Toulbar2 lowest energy:\tFALSE" )
if toulbar2_solution == best_rosetta_solution :
    print(  "Rosetta best is Toulbar2 lowest energy:\tTRUE" )
else :
    print(  "Rosetta best is Toulbar2 lowest energy:\tFALSE" )
print( "Solution space size:\t", np.prod( nodeindex_to_nrotamers ) )