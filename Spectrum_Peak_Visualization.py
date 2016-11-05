import matplotlib.pyplot as plt
import SPEFile
from ROI_Maker import ROI_Maker

def plot_spectrum(spectrum, title= None, energy_range= None):
    """
    plot_spectrum plots the spectra only.
    """
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    counts = spectrum.data

    plt.semilogy(energy_axis, counts, drawstyle='steps-mid')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')
    
    if title != None:      
        plt.title(title)

    if energy_range != None:
        plt.xlim([energy_range[0], energy_range[1]])


def plot_peaks(spectrum, title= None, energy_range= None, subregion='both'):
    """
    plot_peaks plots spectra with peaks highlighted.
    """
    if title != None:
        plt.title(title)
    
    counts = spectrum.data    
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    plt.plot(energy_axis, counts)
    
    if subregion == 'both':
    
        ROI_info = ROI_Maker(spectrum, subregion)
        center_peak_region = ROI_info[2]
        left_peak_region = ROI_info[3]
        right_peak_region = ROI_info[4]   
        
        for i in range(int(len(center_peak_region)/2)):
            plt.fill_between(energy_axis, counts, 
            where=(energy_axis >= energy_axis[center_peak_region[2*i]]) &
            (energy_axis <= energy_axis[center_peak_region[2*i+1]]), 
            facecolor='r')
            plt.fill_between(energy_axis, counts, 
            where= (energy_axis >= energy_axis[left_peak_region[2*i]]) &
            (energy_axis <= energy_axis[left_peak_region[2*i+1]]), 
            facecolor='g')
            plt.fill_between(energy_axis, counts, 
            where= (energy_axis >= energy_axis[right_peak_region[2*i]]) &
            (energy_axis <= energy_axis[right_peak_region[2*i+1]]), 
            facecolor='g')
        
    if subregion in ['left', 'right']:
        
        ROI_info = ROI_Maker(spectrum, subregion)
        center_peak_region = ROI_info[2]
        compton_region = ROI_info[3]
        
        for i in range(int(len(center_peak_region)/2)):
            plt.fill_between(energy_axis, counts, 
            where=(energy_axis >= energy_axis[center_peak_region[2*i]]) &
            (energy_axis <= energy_axis[center_peak_region[2*i+1]]) , 
            facecolor='r')
            plt.fill_between(energy_axis, counts, 
            where= (energy_axis >= energy_axis[compton_region[2*i]]) &
            (energy_axis <= energy_axis[compton_region[2*i+1]]), facecolor='g')
        
    plt.yscale('log')

    if energy_range != None:
        plt.xlim([energy_range[0], energy_range[1]])


def test1():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_spectrum(measurement, 'UCB006_Bananas')

def test2():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_spectrum(measurement, 'UCB006_Bananas', (1450,1470))

def test3():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB006_Bananas')

def test4():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB006_Bananas', subregion='left')
    
def test5():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB006_Bananas', subregion='right')

def test6():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB006_Bananas', (1450,1470), subregion='right')