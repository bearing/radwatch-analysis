from __future__ import print_function
from SpectrumFileBase import SpectrumFileBase
import SPEFile
import numpy as np
import peakutils as p
import os
import pandas as pd
import Gamma_Analysis as ga
import radionuclide_scraper as rs
import Isotopic_Abudance as ia


def peak_finder(measurement):
    """
    peak_finder takes a measurement and returns all of the energies where a
    peak is found.
    """
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
                        peaks_found.append(energy_axis[index + start])
                    else:
                        pass
                start += increment
                end = start + increment
            else:
                start += 1
                end = start + increment
    return peaks_found


def count_rate(M, B, energy):
    """
    Takes in a measured and background spectra and a peak energy and return the
    net area under the peak.

    Peak measurements are done using the Gamma_Analysis peak_measurement
    module, which only does regions of interest. Since peak fitting is not done
    the given count_rate is expected to be systematically higher.
    """
    pm_results = ga.peak_measurement(M, energy, sub_regions='none')
    bm_results = ga.peak_measurement(B, energy, sub_regions='none')
    sub_peak = ga.background_subtract(pm_results, bm_results, M.livetime,
                                      B.livetime)
    net_area = sub_peak[0]
    count_rate = net_area/M.livetime

    return(count_rate)


def isotope_verifier(isotope):
    """
    Takes in an isotope and checks to see whether or not the isotope is
    naturally occuring or not. If the isotope is naturally occuring, then the
    module will indicate that the isotope is naturally occurring and return
    the isotope mass number, isotopic abundance, and radiative capture
    cross section.

    Meta-stable elements are considered the same isotope as the non-meta
    version and has the m removed from the beginning of the name in order to
    allow it to be searched.
    """
    isotope = isotope.symbol + str(isotope.mass_number - 1)
    if isotope[0] == 'm':
        isotope = isotope[1:]
    flag = False

    for i in range(len(ia.natural_isotope_list)):
        var = (ia.natural_isotope_list[i].symbol +
               str(ia.natural_isotope_list[i].mass_number))
        if isotope == var:
            isotope_info = (ia.natural_isotope_list[i].mass_number,
                            ia.natural_isotope_list[i].isotopic_abundance,
                            ia.natural_isotope_list[i].cross_section)
            flag = True
            break

    if flag is False:
        isotope_info = [0, 0, 0]

    return(flag, isotope_info[0], isotope_info[1], isotope_info[2])


def element_fraction(d_per_s, isotope, mass_number, I_A, cross_section,
                     flux, delta, t_irrad, weight):
    N_0 = 6.022 * 10**23
    """cross section, decay constant, isotopic abundance, atomic weight
       will be obtained from an isotope class"""
    first = d_per_s * mass_number / (N_0 * weight * I_A)
    second = first * isotope.decay_constant**(-1)
    third = second * np.exp(delta * isotope.decay_constant)
    fourth = third / (flux * (cross_section * 10**-24) * t_irrad)
    return fourth


def sample_questions():
    """
    sample_questions prompts the user to input information required for
    NAA analysis. This includes sample weight, reactor flux, irradiation time,
    and time between irradiation and measurement.
    """
    weight = input('\n''Enter sample mass in grams.' '\n' '-->')
    weight_value = False
    while weight_value is False:
        try:
            weight = float(weight)
            weight_value = True
        except ValueError:
            print('\n''Please enter a number for mass.''\n')
            weight = input('Enter sample mass in grams.' '\n' '-->')

    flux = input('\n''Enter reactor thermal neutron flux [n/cm2s].' '\n' '-->')
    flux_value = False
    while flux_value is False:
        try:
            flux = float(flux)
            flux_value = True
        except ValueError:
            print('\n''Please enter a number for flux.''\n')
            flux = input('Enter reactor thermal neutron flux [n/cm2s].' '\n'
                         '-->')

    delta_t = input('\n'"Enter the time (in seconds) between the "
                    "irradiation and the measurement." '\n' '-->')
    delta_t_value = False
    while delta_t_value is False:
        try:
            delta_t = float(delta_t)
            delta_t_value = True
        except ValueError:
            print('\n''Please enter a number for time.''\n')
            delta_t = input("Enter the time (in seconds) between the "
                            "irradiation and the measurement." '\n' '-->')

    t_irrad = input('\n''Enter the length of irradiation in seconds.'
                    '\n' '-->')
    t_irrad_value = False
    while t_irrad_value is False:
        try:
            t_irrad = float(t_irrad)
            t_irrad_value = True
        except ValueError:
            print('\n''Please enter a number for irradiation time.''\n')
            t_irrad = input('Enter the length of irradiation in seconds.'
                            '\n' '-->')
    return weight, flux, delta_t, t_irrad


def acquire_measurement():
    """
    acquire_measurement prompts the user to input the measurement file they
    want to analyze.
    """
    measurements = []
    dir_path = os.getcwd()
    for file in os.listdir(dir_path):
        if file.lower().endswith(".spe"):
            measurements.append(file)
    sample = input('\n' "Enter the name of the measurement." '\n'
                   "Please do not include the file extension." '\n' '-->')
    file_found = False
    while file_found is False:
        acquire = sample + '.Spe'
        if acquire in measurements:
            file_found = True
        else:
            print('\n''File not found.''\n')
            sample = input("Enter the name of the measurement." '\n'
                           "Please do not include the file extension." '\n'
                           '-->')
    return acquire

def NAA_table(candidates, energy, isotopes, fractions):
    """
    NAA_table generates a csv file containing the results of the NAA analysis,
    which includes possible isotopes and their fractions for each energy found
    in a certain spectra.
    """
    sorted_info = []
    data = {}
    for i in range(len(isotopes)):
        sorted_info.append((isotopes[i],
                           energy[i],
                           fractions[i]))
    sorted_info = sorted(sorted_info, key=lambda isotope: isotope[0])
    for i in range(len(candidates)):
        data[candidates[i]] = np.array([sorted_info[i][1],
                                        sorted_info[i][0],
                                        sorted_info[i][2]])

    table_headers = []
    table_headers.append('Energy [keV]')
    table_headers.append('Isotope')
    table_headers.append('Mass Fraction')

    frame = pd.DataFrame(data, index=table_headers)
    frame = frame.T
    frame.to_csv('NAA_Results.csv')


def main():
    sample_file = acquire_measurement()
    weight, flux, delta_t, t_irrad = sample_questions()
    measurement = SPEFile.SPEFile(sample_file)
    measurement.read()
    background = SPEFile.SPEFile('USS_Independence_Background.Spe')
    background.read()

    isotopes = []
    energy = []
    candidates = []
    confirmed_energy = []
    confirmed_isotopes = []
    isotope_fraction = []
    count = 0

    energy_peaks = peak_finder(measurement)
    for peak in np.flatnonzero(np.asarray(energy_peaks) > 100):
        energy.append(float(energy_peaks[peak]))
    isotopes = rs.isotope_peaks(energy)
    for energy_peak in range(len(energy)):
        decay_rate = count_rate(measurement, background, energy[energy_peak])
        for isotope in isotopes[energy_peak]:
            flag, mass, abundance, cross_section = isotope_verifier(isotope)
            if flag is False:
                pass
            elif flag is True:
                count += 1
                weight_fraction = element_fraction(decay_rate, isotope,
                                                   mass, abundance,
                                                   cross_section, flux,
                                                   delta_t, t_irrad, weight)
                candidates.append(count)
                confirmed_energy.append(energy[energy_peak])
                confirmed_isotopes.append((isotope.symbol +
                                           str(isotope.mass_number)))
                isotope_fraction.append(weight_fraction)
    NAA_table(candidates, confirmed_energy, confirmed_isotopes,
              isotope_fraction)


if __name__ == '__main__':
    main()
