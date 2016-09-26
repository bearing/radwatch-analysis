import numpy
from matplotlib.pyplot import semilogy
from matplotlib import pyplot as plot

"""
spectrum is a list or a 1D array.
title is a string.
"""

def plot_spectrum(spectrum, title, energy_range = None):
    x = numpy.arange(len(spectrum))
    plot.xlabel('Energy (keV)')
    plot.ylabel('Counts')
    plot.title(title)
    semilogy(x,spectrum,drawstyle='steps-mid')