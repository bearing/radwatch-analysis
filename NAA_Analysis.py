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
N_0 = 6.022 * 10**23

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


def NAA_net_area(measurement, energy):
    """
    NAA_net_area determines the net area of a given peak without the use
    of compton regions. It generates a region of interest (ROI) based on
    full width half maximum (FWHM). A line is generated using the edges of the
    ROI and an integral of the line is determined. The gross counts of the peak
    are then subtracted by the integral and a net area and uncertainty are
    determined and returned.
    """
    E0 = measurement.energy_cal[0]
    Eslope = measurement.energy_cal[1]
    sample_counts = measurement.data
    energy_channel = int((energy - E0) / Eslope)

    region_size = 1.3
    # Rough estimate of FWHM.
    fwhm = 0.05*energy**0.5
    fwhm_channel = int(region_size * (fwhm - E0) / Eslope)
    # peak gross area
    gross_counts_peak = sum(sample_counts[(energy_channel - fwhm_channel):
                                          (energy_channel + fwhm_channel)])
    peak_channels = measurement.channel[(energy_channel - fwhm_channel):
                                        (energy_channel + fwhm_channel)]
    # first and last channel counts of peak
    start_peak_c = sample_counts[(energy_channel - fwhm_channel)]
    end_peak_c = sample_counts[(energy_channel + fwhm_channel)]

    # generate line under peak
    compton_area = (start_peak_c + end_peak_c) / 2 * len(peak_channels)
    net_area = gross_counts_peak - compton_area

    # evaluate uncertainty
    net_area_uncertainty = (gross_counts_peak + compton_area)**0.5
    return net_area, net_area_uncertainty


def peak_decay_rate(M, B, energy, isotope):
    """
    Takes in a measured and background spectra and a peak energy and return the
    net area under the peak.

    Peak measurements are done using the Gamma_Analysis peak_measurement
    module, which only does regions of interest. Since peak fitting is not done
    the given count_rate is expected to be systematically higher.
    """
    efficiency = ga.absolute_efficiency([energy])

    # Find branching ratio for isotope at specified energy
    for isotope_energy in isotope.list_sig_g_e:
        difference = abs(isotope_energy - energy)
        if difference < 3:
            index = isotope.list_sig_g_e.index(isotope_energy)
            break

    branching_ratio = isotope.list_sig_g_b_r[index]

    pm_results = NAA_net_area(M, energy)
    bm_results = ga.peak_measurement(B, energy, sub_regions='none')
    sub_peak = ga.background_subtract(pm_results, bm_results, M.livetime,
                                      B.livetime)
    count_rate = sub_peak[0] / M.livetime
    count_rate_uncertainty = sub_peak[1] / M.livetime

    decay_rate = count_rate / (efficiency[0] * branching_ratio)
    decay_rate_uncertainty = count_rate_uncertainty / (efficiency[0] *
                                                       branching_ratio)

    return [decay_rate, decay_rate_uncertainty, branching_ratio]


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
    """cross section, decay constant, isotopic abundance, atomic weight
       will be obtained from an isotope class"""
    first = d_per_s[0] * mass_number / (N_0 * weight * I_A)
    second = first * isotope.decay_constant**(-1)
    third = second * np.exp(delta * isotope.decay_constant)
    fourth = third / (flux * (cross_section * 10**-24) * t_irrad)

    # Uncertainty calculations
    d_per_s_uncertainty = d_per_s[1]
    flux_uncertainty = flux * 0.1
    delta_uncertainty = 1000
    t_irrad_uncertainty = 1

    d_dd_per_s = fourth / d_per_s[0]
    d_dflux = fourth * (-1 / flux)
    d_dt_irrad = fourth * (-1 / t_irrad)
    d_ddelta = fourth * isotope.decay_constant

    uncertainty = (((d_per_s_uncertainty)**2 * d_dd_per_s**2) *
                   ((flux_uncertainty)**2 * (d_dflux)**2) *
                   ((delta_uncertainty)**2 * (d_ddelta)**2) *
                   ((t_irrad_uncertainty)**2 * (d_dt_irrad)**2))**0.5
    return fourth, uncertainty


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


def NAA_table(candidates, energy, isotopes, fractions, uncertainty):
    """
    NAA_table generates a csv file containing the results of the NAA analysis,
    which includes possible isotopes and their fractions for each energy found
    in a certain spectra.
    """
    sorted_info = []
    data = {}

    # Make a dataset sorted by isotope
    for i in range(len(isotopes)):
        sorted_info.append((isotopes[i],
                           energy[i],
                           fractions[i],
                           uncertainty[i]))
    sorted_info = sorted(sorted_info, key=lambda isotope: isotope[0])
    for i in range(len(candidates)):
        # sorted by isotope
        data[candidates[i]] = np.array([sorted_info[i][1],
                                        sorted_info[i][0],
                                        sorted_info[i][2],
                                        sorted_info[i][3]])

    table_headers = []
    table_headers.append('Energy [keV]')
    table_headers.append('Isotope')
    table_headers.append('Mass Fraction')
    table_headers.append('Fraction Unc.')

    frame = pd.DataFrame(data, index=table_headers)
    frame = frame.T
    frame.to_csv('NAA_Results_Isotope.csv')


def create_cache(candidates, energy, branching_ratios, isotopes, half_lives,
                 mass_number, isotopic_abundance, cross_section):
    """
    create_cache creates an offline database containing all found isotopes
    along with relevant information needed to calculate concentrations using
    the NAA weight fraction formula.
    """
    data_e = {}
    for i in range(len(candidates)):
        # sorted by energy
        data_e[candidates[i]] = np.array([energy[i], isotopes[i],
                                          half_lives[i], branching_ratios[i],
                                          mass_number[i],
                                          isotopic_abundance[i],
                                          cross_section[i]])
    table_headers_e = []
    table_headers_e.extend(['Energy [keV]', 'Isotope', 'Half-life [s]',
                            'Branching Ratio', 'Mass Number',
                            'Isotopic Abundance', 'Cross Section [b]'])
    frame_energy = pd.DataFrame(data_e, index=table_headers_e)
    frame_energy = frame_energy.T
    frame_energy.to_csv('NAA_Results_Energy.csv')



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
    branching_ratio = []
    confirmed_isotopes = []
    isotope_half_life = []
    isotope_mass_number = []
    isotope_abundance = []
    isotope_cross_section = []
    isotope_fraction = []
    fraction_uncertainty = []
    count = 0

    energy_peaks = peak_finder(measurement)
    for peak in np.flatnonzero(np.asarray(energy_peaks) > 100):
        energy.append(float(energy_peaks[peak]))
    isotopes = rs.isotope_peaks(energy)
    for energy_peak in range(len(energy)):
        for isotope in isotopes[energy_peak]:
            flag, mass, abundance, cross_section = isotope_verifier(isotope)
            if flag is False:
                pass
            elif flag is True:
                count += 1
                decay_rate = peak_decay_rate(measurement, background,
                                             energy[energy_peak], isotope)
                weight_fraction, uncertainty = element_fraction(decay_rate,
                                                                isotope,
                                                                mass,
                                                                abundance,
                                                                cross_section,
                                                                flux,
                                                                delta_t,
                                                                t_irrad,
                                                                weight)
                candidates.append(count)
                confirmed_energy.append(energy[energy_peak])
                branching_ratio.append(decay_rate[2])
                isotope_mass_number.append(isotope.mass_number)
                isotope_abundance.append(abundance)
                isotope_cross_section.append(cross_section)
                confirmed_isotopes.append((isotope.symbol +
                                           str(isotope.mass_number)))
                isotope_half_life.append(isotope.half_life)
                isotope_fraction.append(weight_fraction)
                fraction_uncertainty.append(uncertainty)
    NAA_table(candidates, confirmed_energy, confirmed_isotopes,
              isotope_fraction, fraction_uncertainty)
    create_cache(candidates, confirmed_energy, branching_ratio,
                 confirmed_isotopes, isotope_half_life,
                 isotope_mass_number, isotope_abundance, isotope_cross_section)


if __name__ == '__main__':
    main()
