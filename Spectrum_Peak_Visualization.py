import numpy
from matplotlib.pyplot import semilogy
from matplotlib import pyplot as plot

"""
spectrum_array is assumed to be an array. However, if spectrum_array is a list
then the function will automatically convert string into array.
title is a string.
Optional argument energy_range which is a tuple with notation
(energy_min, energy_max) for plotting within a specific energy range.
Default value for energy_range is None.
"""

def plot_spectrum(spectrum_array, energy_per_channel, title, energy_range = None):
    channels = numpy.arange(len(spectrum_array))
    energies = energy_per_channel*channels    
    if type(spectrum_array) == 'list':
            spectrum_array = numpy.array(spectrum_array)  
            
    if energy_range != None:
        min_index = (numpy.abs(energies-energy_range[0])).argmin
        max_index = (numpy.abs(energies-energy_range[1])).argmin
        plot.xlabel('Channels')
        plot.ylabel('Counts')
        plot.title(title)
        semilogy()
        
    else:    
        plot.xlabel('Channels')
        plot.ylabel('Counts')
        plot.title(title)
        semilogy(energies,spectrum_array,drawstyle='steps-mid')