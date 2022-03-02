import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('TkAgg')

def read_file( filename ) :
    with open( filename ) as filehandle:
        lines = filehandle.readlines()
    
    probsizes = np.empty( [len(lines) - 1], dtype=np.int64 )
    toulbar2_times = np.empty( [len(lines) - 1], dtype=np.float64 )
    qpacker_times = np.empty( [len(lines) - 1], dtype=np.float64 )

    #Assume first line is header (i.e. skip line 0).
    for i in range( 1, len(lines) ) :
        linesplit = lines[i].split()
        probsizes[i-1] = int(linesplit[0])
        toulbar2_times[i-1] = float(linesplit[1])
        qpacker_times[i-1] = float(linesplit[2])
    
    return probsizes, toulbar2_times, qpacker_times


# Problems where the QPacker finds the lowest-energy solution:
probsizes_solved, toulbar2_times_solved, qpacker_times_solved = read_file( "summary_lowestE.txt" )

# Problems where the QPacker doesn't find the lowest-energy solution:
probsizes_notsolved, toulbar2_times_notsolved, qpacker_times_notsolved = read_file( "summary_not_lowestE.txt" )

# Concatenated:
probsizes_all = np.concatenate( (probsizes_solved, probsizes_notsolved) )
toulbar2_times_all = np.concatenate( (toulbar2_times_solved, toulbar2_times_notsolved) )

#Plotting
plt.scatter( probsizes_all, toulbar2_times_all, c='blue', marker=".", s=50 )
#plt.scatter( probsizes_notsolved, qpacker_times_notsolved, c='None', edgecolor='red', marker=".", s=50, linewidth=0.25 )
plt.scatter( probsizes_solved, qpacker_times_solved, c='red', marker=".", s=50 )
plt.yscale('log')
plt.xscale('log')
plt.xlabel( "Size of solution space\n(number of possible solutions)" )
plt.ylabel( r"Average time to find lowest-energy solution ($\mu$s)" )
plt.show()
