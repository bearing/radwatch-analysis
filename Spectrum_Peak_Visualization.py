import numpy as np
import matplotlib.pyplot as plt
import peakutils
import SPEFile

"""
plot_spectrum plots the spectra only.
"""
def plot_spectrum(spectrum, title,energy_range='None'):
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    counts = spectrum.data
    
    #Graphs the spectrum first without any ROIs.
    plt.semilogy(energy_axis,counts,drawstyle='steps-mid')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')
    plt.title(title)
    
    """
    If energy_range is set to a tuple of two values, then below code will graph
    the spectrum within the energy_range values for the energies (x-values).
    """    
    if energy_range != 'None':
        plt.xlim([energy_range[0], energy_range[1]])


"""
plot_peaks plots spectra with peaks highlighted.
"""
def plot_peaks(spectrum,title,energy_range='None'):
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    counts = spectrum.data
    
    #Graphs the spectrum first without any ROIs.
    plt.plot(energy_axis,counts,drawstyle='steps-mid')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')
    plt.title(title)
    
    """
    Need to call Jackie's peak finder function to get indices of the peaks and
    place those indices in a list for use in highlighting ROIs below. 
    Currently, Chris's code, below, is being used for testing purposes for 
    highlighting peaks.
    """
    found_energy = []
    peak_channel = []
    energy_list = [351.93, 583.19, 609.31, 911.20, 1120.29, 1460.82, 1764.49,
                   2614.51]
    skip = 0
    fix = 0
    for energy in energy_list:
        # Rough estimate of FWHM.
        fwhm = 0.05*energy**0.5
        Range = 0.015*energy

        # Peak Gross Area

        start_region = np.flatnonzero(energy_axis > energy - Range)[0]

        end_region = np.flatnonzero(energy_axis > energy + Range)[0]
        y = spectrum.data[start_region:end_region]
        indexes = peakutils.indexes(y, thres=0.5, min_dist=4)
        tallest_peak = []
        if indexes.size == 0:
            print('Peak Not Found')
            skip += 1
        else:
            for i in range(indexes.size):
                spot = spectrum.data[indexes[i]+start_region]
                tallest_peak.append(spot)
            indexes = indexes[np.argmax(tallest_peak)]
            peak_channel.append(int(indexes+start_region))
            found_energy.append(energy)
            difference = abs((energy -
                              float(energy_axis[int(indexes+start_region)])))
            if difference > 0.5*fwhm:
                fix += 1

    """
    Below is code directly from gamma analysis; have to modify the code to work
    with code within the function.Loop through this code to obtain peak and 
    background ROIs for each peak energy. Afterwards, will highlight each peak 
    ROI as red and background ROI as green.
    """
    for energy in found_energy:
        # Rough estimate of FWHM.
        fwhm = 0.05*energy**0.5
        
        # Peak
        start_peak = np.flatnonzero(energy_axis > energy - fwhm)[0]
        end_peak = np.flatnonzero(energy_axis > energy + fwhm)[0]
        plt.fill_between(energy_axis,counts,
                         where= (energy_axis >= energy_axis[start_peak]) &
                         (energy_axis <= energy_axis[end_peak]),facecolor='r')
        
        # Left Side of Peak
        left_peak = energy - 2*fwhm
        left_start = np.flatnonzero(energy_axis > left_peak - fwhm)[0]
        left_end = np.flatnonzero(energy_axis > left_peak + fwhm)[0]
        plt.fill_between(energy_axis,counts,
                         where= (energy_axis >= energy_axis[left_start]) &
                         (energy_axis <= energy_axis[left_end]),facecolor='g')
        
        # Right Side of Peak
        right_peak = energy + 2*fwhm
        right_start = np.flatnonzero(energy_axis > right_peak - fwhm)[0]
        right_end = np.flatnonzero(energy_axis > right_peak + fwhm)[0]
        plt.fill_between(energy_axis,counts,
                         where= (energy_axis >= energy_axis[right_start]) &
                         (energy_axis <= energy_axis[right_end]),facecolor='g')
        
    #Converting the y-axis to semilog.    
    plt.yscale('log')
    
    """
    If energy_range is set to a tuple of two values, then below code will graph
    the spectrum with the highlighted peaks and background within the 
    energy_range values for the energies (x-values).
    """    
    if energy_range != 'None':
        plt.xlim([energy_range[0], energy_range[1]])

"""
#Test 1 for plot_spectrum
measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
measurement.read()
plot_spectrum(measurement, 'UCB006_Bananas')
"""
"""
#Test 2 for plot_spectrum
measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
measurement.read()
plot_spectrum(measurement, 'UCB006_Bananas',(2606,2626))
"""
"""
#Test 3 for plot_peaks
measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
measurement.read()
plot_peaks(measurement, 'UCB006_Bananas')
"""
"""
#Test 4 for plot_peaks
measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
measurement.read()
plot_peaks(measurement, 'UCB006_Bananas',(2606,2626))
"""