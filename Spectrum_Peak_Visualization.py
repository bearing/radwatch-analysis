"""
In order to run this file, it is necessary to install PeakUtils. 
Instructions are located in the link below. 
https://pypi.python.org/pypi/PeakUtils
-Tyler
"""
import matplotlib.pyplot as plt
import SPEFile
from ROI_Maker import ROI_Maker
import numpy as np


def plot_spectrum(spectrum, title=None, energy_range=None):
    """
    plot_spectrum plots the spectra only.
    """
    font = {'size': 20}
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    counts = spectrum.data

    plt.semilogy(energy_axis, counts, drawstyle='steps-mid')
    plt.xlim(xmin=0)
    plt.xlabel('Energy (keV)', fontdict=font)
    plt.ylabel('Counts', fontdict=font)

    if title is not None:
        plt.title(title, fontdict=font)

    if energy_range is not None:
        plt.xlim([energy_range[0], energy_range[1]])


def plot_peaks(spectrum, title=None, energy_range=None, subregion='both',
               use='GA', peak_location=[]):
    """
    plot_peaks plots spectra with peaks highlighted.
    """
    if title is not None:
        plt.title(title)

    counts = spectrum.data
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel * spectrum.channel
    plt.plot(energy_axis, counts)

    ROI_info = ROI_Maker(spectrum, use, peak_location)
    center_peak_region = ROI_info[2]
    left_peak_region = ROI_info[3]
    right_peak_region = ROI_info[4]

    if subregion == 'NAA':

        for i in range(int(len(center_peak_region) / 2)):
            start_region = energy_axis[center_peak_region[2 * i]]
            end_region = energy_axis[center_peak_region[2 * i + 1]]
            start_region_counts = counts[center_peak_region[2 * i]]
            end_region_counts = counts[center_peak_region[2 * i + 1]]
            l = [start_region, end_region]
            m = [start_region_counts, end_region_counts]
            a_matrix = np.vstack([l, np.ones(2)]).T
            slope, intercept = np.linalg.lstsq(a_matrix, m)[0]

            x = np.arange(start_region, end_region, 0.001)
            y = []
            for j in range(len(x)):
                y.append(slope*x[j] + intercept)

            plt.plot(x, y)
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[center_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[center_peak_region[2 * i + 1]]),
                             facecolor='r')
            plt.fill_between(x, y, facecolor='b')

    if subregion == 'peak':

        for i in range(int(len(center_peak_region)/2)):
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[center_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[center_peak_region[2 * i + 1]]),
                             facecolor='r')

    if subregion == 'both':

        for i in range(int(len(center_peak_region) / 2)):
            flag = False
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[center_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[center_peak_region[2 * i + 1]]),
                             facecolor='r')
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[left_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[left_peak_region[2 * i + 1]]),
                             facecolor='g')

            if (energy_axis[center_peak_region[2 * i]] <= 604.72 <=
                    energy_axis[center_peak_region[2 * i + 1]]):
                flag = True

            if flag is False:
                plt.fill_between(energy_axis, counts, where=(energy_axis >=
                                 energy_axis[right_peak_region[2 * i]]) &
                                 (energy_axis <=
                                 energy_axis[right_peak_region[2 * i + 1]]),
                                 facecolor='g')

    if subregion == 'left':

        for i in range(int(len(center_peak_region) / 2)):
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[center_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[center_peak_region[2 * i + 1]]),
                             facecolor='r')
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[left_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[left_peak_region[2 * i + 1]]),
                             facecolor='g')

    if subregion == 'right':

        for i in range(int(len(center_peak_region) / 2)):
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[center_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[center_peak_region[2 * i + 1]]),
                             facecolor='r')
            plt.fill_between(energy_axis, counts, where=(energy_axis >=
                             energy_axis[right_peak_region[2 * i]]) &
                             (energy_axis <=
                             energy_axis[right_peak_region[2 * i + 1]]),
                             facecolor='g')
<<<<<<< HEAD
    if energy_range is not None:
        plt.xlim([energy_range[0], energy_range[1]])
=======
   
    plt.xlim(xmin=0)
>>>>>>> refs/remotes/origin/master
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')


def test1():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_spectrum(measurement, 'UCB006_Bananas')

def test2():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_spectrum(measurement, 'UCB006_Bananas', (1450, 1470))

def test3():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB018_Soil_Sample010_2')

def test4():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB018_Soil_Sample010_2', subregion='left')

def test5():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB018_Soil_Sample010_2', subregion='right')

def test6():
    measurement = SPEFile.SPEFile('UCB006_Bananas.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB006_Bananas', (1450, 1470), subregion='right')

def test7():
    measurement = SPEFile.SPEFile('UCB065_Halibut.Spe')
    measurement.read()
    plot_peaks(measurement, 'UCB065_Halibut', subregion='both', use='GA')

def test8():
    measurement = SPEFile.SPEFile('C17-01.Spe')
    measurement.read()
    plot_peaks(measurement, 'C17-01', subregion='NAA', use='NAA')

def test9():
    measurement = SPEFile.SPEFile('Unknown-sample.Spe')
    measurement.read()
    plot_peaks(measurement, 'Unknown-sample', subregion='NAA', use='NAA')
