import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt
import math

#matplotlib.use('TkAgg')

def fit_func(x,m,b):
    #return m*x+b
    return np.exp(m*np.log(x)+b)
    #return np.power(m*np.log(x),b)
    #return np.add(np.exp(m*np.log(x)+b),c)

def split_solutions( probsizes_all, times_all, finds_lowest ) :
    assert len(probsizes_all) == len(times_all)
    assert len(probsizes_all) == len(finds_lowest)

    probsizes_solved = []
    probsizes_unsolved = []
    times_solved = []
    times_unsolved = []

    for i in range(len(probsizes_all)) :
        if finds_lowest[i] == True :
            probsizes_solved.append( probsizes_all[i] )
            times_solved.append( times_all[i] )
        else :
            probsizes_unsolved.append( probsizes_all[i] )
            times_unsolved.append( times_all[i] )

    return np.array( probsizes_solved, dtype=np.int64 ), \
        np.array( times_solved, dtype=np.float64 ), \
        np.array( probsizes_unsolved, dtype=np.int64 ), \
        np.array( times_unsolved, dtype=np.float64 )

def parse_float( floatstr : str ) -> float :
    if floatstr == "N/A" :
        return 999999.9
    return float( floatstr )

# Reads a datafile with columns:
# $solsize $ttime $qtime $q2000time $rtime $qbestislowest $q2000bestislowest $rbestislowest
def read_file( filename : str ) :
    with open( filename ) as filehandle:
        lines = filehandle.readlines()
    
    probsizes = np.empty( [len(lines) - 1], dtype=np.int64 )
    toulbar2_times = np.empty( [len(lines) - 1], dtype=np.float64 )
    qpacker_times = np.empty( [len(lines) - 1], dtype=np.float64 )
    qpacker_2000q_times = np.empty( [len(lines) - 1], dtype=np.float64 )
    rosetta_times = np.empty( [len(lines) - 1], dtype=np.float64 )
    qpacker_finds_lowest = np.empty( [len(lines) - 1], dtype=bool )
    qpacker_2000q_finds_lowest = np.empty( [len(lines) - 1], dtype=bool )
    rosetta_finds_lowest = np.empty( [len(lines) - 1], dtype=bool )

    #Assume first line is header (i.e. skip line 0).
    for i in range( 1, len(lines) ) :
        linesplit = lines[i].split()
        probsizes[i-1] = int(linesplit[0])
        toulbar2_times[i-1] = float(linesplit[1])
        qpacker_times[i-1] = parse_float( linesplit[2] )
        qpacker_2000q_times[i-1] = parse_float( linesplit[3] )
        rosetta_times[i-1] = parse_float( linesplit[4] )

        if linesplit[5] == "TRUE" :
            qpacker_finds_lowest[i-1] = True
        else :
            qpacker_finds_lowest[i-1] = False

        if linesplit[6] == "TRUE" :
            qpacker_2000q_finds_lowest[i-1] = True
        else :
            qpacker_2000q_finds_lowest[i-1] = False

        if linesplit[7] == "TRUE" :
            rosetta_finds_lowest[i-1] = True
        else :
            rosetta_finds_lowest[i-1] = False
    
    return probsizes, toulbar2_times, qpacker_times, qpacker_2000q_times, rosetta_times, qpacker_finds_lowest, qpacker_2000q_finds_lowest, rosetta_finds_lowest


print( "Reading summary.txt.", flush=True )
probsizes_all, toulbar2_times_all, qpacker_times_all, qpacker_2000q_times_all, \
    rosetta_times_all, qpacker_finds_lowest, qpacker_2000q_finds_lowest, rosetta_finds_lowest = \
    read_file( "summary.txt" )

print( "Splitting QPacker Advantage solutions.", flush=True )
probsizes_qpacker_solved, qpacker_times_solved, probsizes_qpacker_unsolved, qpacker_times_unsolved = \
    split_solutions( probsizes_all, qpacker_times_all, qpacker_finds_lowest )
print( "Splitting QPacker 2000Q solutions.", flush=True )
probsizes_qpacker_2000q_solved, qpacker_2000q_times_solved, probsizes_qpacker_2000q_unsolved, qpacker_2000q_times_unsolved = \
    split_solutions( probsizes_all, qpacker_2000q_times_all, qpacker_2000q_finds_lowest )
print( "Splitting Rosetta solutions.", flush=True )
probsizes_rosetta_solved, rosetta_times_solved, probsizes_rosetta_unsolved, rosetta_times_unsolved = \
    split_solutions( probsizes_all, rosetta_times_all, rosetta_finds_lowest )

# Problems where the QPacker finds the lowest-energy solution:
#probsizes_solved, toulbar2_times_solved, qpacker_times_solved, rosetta_times_solved, rosetta_finds_lowest_solved = read_file( "summary_lowestE.txt" )

# Problems where the QPacker doesn't find the lowest-energy solution:
#probsizes_notsolved, toulbar2_times_notsolved, qpacker_times_notsolved, rosetta_times_notsolved, rosetta_finds_lowest_notsolved = read_file( "summary_not_lowestE.txt" )

# Concatenated:
#probsizes_all = np.concatenate( (probsizes_solved, probsizes_notsolved) )
#toulbar2_times_all = np.concatenate( (toulbar2_times_solved, toulbar2_times_notsolved) )
#rosetta_times_all = np.concatenate( (rosetta_times_solved, rosetta_times_notsolved) )
#rosetta_finds_lowest_all = np.concatenate( (rosetta_finds_lowest_solved, rosetta_finds_lowest_notsolved) )
# rosetta_markers = np.empty( len(rosetta_finds_lowest_all), dtype=object )
# for i in range( len(rosetta_finds_lowest_all) ) :
#     if( rosetta_finds_lowest_all[i] == True ) :
#         rosetta_markers[i] = "."
#     else :
#         rosetta_markers[i] = "o"

#Plotting
fig = plt.figure( figsize=(5,5), dpi=300 )
plt.scatter( probsizes_qpacker_2000q_solved, qpacker_2000q_times_solved, c='brown', marker=".", s=25, label="QPacker on D-Wave 2000Q" )
#plt.scatter( probsizes_qpacker_2000q_unsolved, qpacker_2000q_times_unsolved, c='brown', marker="o", s=25 )
plt.scatter( probsizes_qpacker_solved, qpacker_times_solved, c='orange', marker=".", s=25, label="QPacker on D-Wave Advantage" )
#plt.scatter( probsizes_qpacker_unsolved, qpacker_times_unsolved, c='orange', marker="o", s=25 )
plt.scatter( probsizes_all, toulbar2_times_all, c='cyan', marker=".", s=25, label="Toulbar2 branch-and-bound" )
plt.scatter( probsizes_rosetta_solved, rosetta_times_solved, c='purple', marker=".", s=25, label="Rosetta simulated annealer" )
#plt.scatter( probsizes_unsolved, rosetta_times_unsolved, c='purple', marker="o", s=25 )
plt.yscale('log')
plt.xscale('log')
plt.xlabel( "Size of solution space (number of possible solutions)" )
plt.ylabel( r"Average time to find lowest-energy solution ($\mu$s)" )

# Exponential fit:
# toulbar2_times_all_uncertainty = np.ones( len(probsizes_all), dtype=np.float64 ) #Uncertainty is constant for Toulbar2
# toulbar2_fit, toulbar2_cov = opt.curve_fit( fit_func, probsizes_all, toulbar2_times_all, [1, 1], sigma=toulbar2_times_all_uncertainty, absolute_sigma=False )
# qpacker_times_solved_uncertainty = np.power( qpacker_times_solved, 2 ) #Uncertainty is propotional to time squared for QPacker (see note below).
# qpacker_solved_fit, qpacker_solved_cov = opt.curve_fit( fit_func, probsizes_qpacker_solved, qpacker_times_solved, [1, 1], sigma=qpacker_times_solved_uncertainty, absolute_sigma=False )
# qpacker_2000q_times_solved_uncertainty = np.power( qpacker_2000q_times_solved, 2 ) #Uncertainty is propotional to time squared for QPacker (see note below).
# qpacker_2000q_solved_fit, qpacker_2000q_solved_cov = opt.curve_fit( fit_func, probsizes_qpacker_2000q_solved, qpacker_2000q_times_solved, [1, 1], sigma=qpacker_2000q_times_solved_uncertainty, absolute_sigma=False )
# rosetta_times_solved_uncertainty = np.power( rosetta_times_solved, 2 ) #Uncertainty is propotional to time squared for Rosetta (see note below).
# rosetta_solved_fit, rosetta_solved_cov = opt.curve_fit( fit_func, probsizes_rosetta_solved, rosetta_times_solved, [1, 1], sigma=rosetta_times_solved_uncertainty, absolute_sigma=False )
# plotrange_all = np.logspace( math.log(min(probsizes_all), 10), math.log(max(probsizes_all), 10), 150, dtype=np.float64, base=10 )
# plotrange_qpacker_solved = np.logspace( math.log(min(probsizes_qpacker_solved), 10), math.log(max(probsizes_qpacker_solved), 10), 150, dtype=np.float64, base=10 )
# plotrange_qpacker_2000q_solved = np.logspace( math.log(min(probsizes_qpacker_2000q_solved), 10), math.log(max(probsizes_qpacker_2000q_solved), 10), 150, dtype=np.float64, base=10 )
# plotrange_rosetta_solved = np.logspace( math.log(min(probsizes_rosetta_solved), 10), math.log(max(probsizes_rosetta_solved), 10), 150, dtype=np.float64, base=10 )
# plt.plot( plotrange_all, fit_func( plotrange_all, *toulbar2_fit ), '-', c='cyan', linewidth=2 )
# plt.plot( plotrange_qpacker_solved, fit_func( plotrange_qpacker_solved, *qpacker_solved_fit ), '-', c='orange', linewidth=2 )
# plt.plot( plotrange_qpacker_2000q_solved, fit_func( plotrange_qpacker_2000q_solved, *qpacker_2000q_solved_fit ), '-', c='brown', linewidth=2 )
# plt.plot( plotrange_rosetta_solved, fit_func( plotrange_rosetta_solved, *rosetta_solved_fit ), '-', c='purple', linewidth=2 )

# Legend:
plt.legend( loc="upper right" )

fig.subplots_adjust(bottom=0.12, top=0.975, hspace=0.3, left=0.12, right=0.975, wspace=0.2)
#plt.show()
fig.savefig( "plot.pdf" )

# Note on uncertainty for Qpacker:
# t_expected = t_sample / fract_good = t_total / N_samples * N_samples / N_good = t_total / N_good
# Assuming uncertainty in t_total is negligable,
# Delta t_expected / t_expected = -t_total*(Delta N_good)/N_good
# Delta t_expected = -t_expected * t_total * (Delta N_good) / (t_total / t_expected)
# Delta t_expected = -t_expected^2 * (Delta N_good)
# Since Delta N_good is a constant, Delta t_expected is proportional to t_expected squared.