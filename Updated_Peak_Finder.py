from __future__ import print_function
import numpy as np
import peakutils as p
import matplotlib.pyplot as plt
import SPEFile


def peak_finder_pro(measurement):
    E0 = measurement.energy_cal[0]
    Eslope = measurement.energy_cal[1]
    energy_axis = E0 + Eslope*measurement.channel
    increment = 25
    counts = measurement.data
    peaks_found = []
    plop = []
    start = 0
    end = start + increment
    count = 0
    for energy in energy_axis:
        count += 1
        if end >= len(measurement.channel):
            break
        else:
            count_total = sum(counts[start:end])
            average_range = count_total / (len(counts[start:end]))
            average_ends = (counts[start] + counts[end]) / 2
            threshold = 1.1 * average_ends
            if average_range > threshold:
                counts_range = counts[start:end]
                middle = int((start + end) / 2)
                average_fwhm = 0.05 * energy_axis[middle]**0.5
                average_fwhm_dist = int(average_fwhm / Eslope)
                indexes = p.indexes(np.log(counts_range),
                                    thres=0.1, min_dist=average_fwhm_dist)
                for index in indexes:
                    plop.append(index+start)
                    uncertainty = average_range**0.5
                    significance = ((counts[start+index]-average_range) /
                                    uncertainty)
                    if significance > 4:
                        peaks_found.append(index + start)
                    else:
                        pass
                start += 25
                end = start + increment
            else:
                start += 1
                end = start + increment
    return peaks_found
    print(peaks_found)
    print(count)
    print(len(peaks_found))
    plt.figure()
    plt.title('Filtered Peaks')
    plt.plot(measurement.channel, np.log(counts))
    plt.plot(measurement.channel[peaks_found],
             np.log(counts[peaks_found]), 'ro')
    plt.figure()
    plt.title('All Peaks')
    plt.plot(measurement.channel, np.log(counts))
    plt.plot(measurement.channel[plop], np.log(counts[plop]), 'bo')
    plt.show()
measurement = SPEFile.SPEFile('Sample_12_Second_Long_Run.Spe')
measurement.read()
peak_found = peak_finder_pro(measurement)
