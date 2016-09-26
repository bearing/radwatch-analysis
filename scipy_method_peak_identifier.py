"""
This component of the gamma_analysis code is in charge of identifying peaks
in a given energy spectra. The peaks are identified by the difference in counts
relative to its surrounding bins.
"""
from __future__ import print_function
import numpy as np
import math as mt
from matplotlib import pyplot as mpl
from scipy import signal
import matplotlib.pyplot as plt


def peak_finder_pro(measurement):
    E0 = measurement.energy_cal[0]
    slope = measurement.energy_cal[1]
    energy_axis = measurement.channel
    energy_axis = energy_axis.astype(float)
    energy_axis[:] = [E0 + slope * x for x in range(len(measurement.channel))]

    """energy_spectra is the spectra that will be loaded and analyzed"""

    fwhm_list = []
    for i in energy_axis:
        fwhm = 0.05 * energy_axis[i] ** 0.5
        fwhm_list = fwhm_list.append(fwhm)

    counts = measurement.data

    peaks_found = []
    start = 0
    end = start + 50
    for energy in energy_axis:
        E_start = energy_axis[start]
        E_end = energy_axis[end]
        energy_range = range(E_start, E_end)
        count_total = 0
        for i in energy_range:
            count_total = count_total + counts[energy_range[i]]
        avg_range = count_total/len(energy_range)
        avg_ends = (counts[start] + counts[end]) / 2
        threshold = 1.1 * avg_ends
        if avg_range > threshold:
            energy_average = start + 25
            avg_fwhm = fwhm_list[energy_average]
            width_parameter = avg_fwhm * 3
            wavelet = signal.ricker(width_parameter, avg_fwhm)
            counts_range = range(counts[E_start], counts[E_end])
            wave_transform = signal.cwt(counts_range, wavelet, width_parameter)
            peak_finder = signal.find_peaks_cwt(wave_transform, counts_range)
            peaks_found.append(peak_finder)
            next_range = peak_finder + 0.5 * avg_fwhm
            start = next_range
        else:
            start += 1
        return peaks_found


measurement = SPEFile.SPEFile('USS_Independence_Background.Spe')
measurement.read()
peak_found = peak_finder_pro(measurement)
print(peak_found)
