import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt
import math

matplotlib.use('TkAgg')

def fit_func(x,m,b):
    #return m*x+b
    return np.exp(m*np.log(x)+b)

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

# Power fit:
toulbar2_times_all_uncertainty = np.power( toulbar2_times_all, 1 ) #Uncertainty is propotional to time for Toulbar2
toulbar2_fit, toulbar2_cov = opt.curve_fit( fit_func, probsizes_all, toulbar2_times_all, [1, 1], sigma=toulbar2_times_all_uncertainty, absolute_sigma=False )
toulbar2_fit, toulbar2_cov = opt.curve_fit( fit_func, probsizes_all, toulbar2_times_all, [1, 1] )
qpacker_times_solved_uncertainty = np.power( qpacker_times_solved, 2 ) #Uncertainty is propotional to time squared for QPacker (see note below).
qpacker_solved_fit, qpacker_solved_cov = opt.curve_fit( fit_func, probsizes_solved, qpacker_times_solved, [1, 1], sigma=qpacker_times_solved_uncertainty, absolute_sigma=False )
plotrange_all = np.logspace( math.log(min(probsizes_all), 10), math.log(max(probsizes_all), 10), 150, dtype=np.float64, base=10 )
plotrange_solved = np.logspace( math.log(min(probsizes_solved), 10), math.log(max(probsizes_solved), 10), 150, dtype=np.float64, base=10 )
plt.plot( plotrange_all, fit_func( plotrange_all, *toulbar2_fit ), '--', c='blue', linewidth=2 )
plt.plot( plotrange_solved, fit_func( plotrange_solved, *qpacker_solved_fit ), '--', c='red', linewidth=2 )

plt.show()


# Note on uncertainty for Qpacker:
# t_expected = t_sample / fract_good = t_total / N_samples * N_samples / N_good = t_total / N_good
# Assuming uncertainty in t_total is negligable,
# Delta t_expected / t_expected = -t_total*(Delta N_good)/N_good
# Delta t_expected = -t_expected * t_total * (Delta N_good) / (t_total / t_expected)
# Delta t_expected = -t_expected^2 * (Delta N_good)
# Since Delta N_good is a constant, Delta t_expected is proportional to t_expected squared.