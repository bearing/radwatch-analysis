"""
This will perform a gamma analysis
It will collect two spectra:
M = Measurement Spectrum
B = Background Spectrum
"""
from __future__ import print_function
from SpectrumFileBase import SpectrumFileBase
import Gamma_Isotopes as ii
import Gamma_Reference as ref
import SPEFile
import numpy as np
import matplotlib.pyplot as plt
import peakutils
import pandas as pd
import os

EFFICIENCY_CAL_COEFFS = [-5.1164, 161.65, -3952.3, 30908]


def absolute_efficiency(energy, coeffs=EFFICIENCY_CAL_COEFFS):
    """
    Returns absolute efficiencies for a given set of energies, based on a
    provided efficiency calibration. It takes an energy (in keV) and a set
    of calibration coefficients.
    The efficiency is calculated using the equation given below:
    ln(efficiency) = c3*(E^3) + c2*(E^2) + c1*E + c0*E,
    where E = ln(energy[keV])/energy[keV]
    """
    efficiency = []
    for i in range(len(energy)):
        efficiency.append(np.exp(coeffs[3] *
                          (np.log(energy[i])/energy[i])**3 +
                          coeffs[2]*(np.log(energy[i])/energy[i])**2 +
                          coeffs[1]*(np.log(energy[i])/energy[i]) +
                          coeffs[0]))
    return efficiency


def emission_rate(net_area, efficiency, livetime):
    """
    this function returns the emission rate of gammas per second
    alongside its uncertainty.
    """
    emission_rate = [net_area[0]/(efficiency*livetime),
                     net_area[1]/(efficiency*livetime)]
    return emission_rate


def isotope_activity(isotope, emission_rates, emission_uncertainty):
    """
    Isotope_Activity will determine the activity of a given radioactive isotope
    based on the emission rates given and the isotope properties. It takes an
    Isotope object and a given set of emission rates and outputs an activity
    estimate alongside its uncertainty.
    """
    branching_ratio = isotope.list_sig_g_b_r
    activity = []
    uncertainty = []
    for i in range(len(branching_ratio)):
        activity.append(emission_rates[i] / (0.01 * branching_ratio[i]))
        uncertainty.append(emission_uncertainty[i] /
                           (0.01 * branching_ratio[i]))
    isotope_activity = np.mean(activity)
    activity_uncertainty = np.mean(uncertainty)
    results = [isotope_activity, activity_uncertainty]
    return results


def isotope_concentration(isotope, reference, sample_activity,
                          reference_activity):
    """
    Isotope_Concentration evaluates the concentration of a certain isotope
    given a reference sample and reference along with their respective
    activities. The Reference contains information regarding the concentrations
    of isotopes and their uncertainties. A reference activity per mass is
    calculated and a ratio of specific activity and concentration is
    determined. The sample activity is multiplied by this ratio and a
    conversion factor that is contained in the Reference. The Reference and
    isotope are objects while their activities are a scalar number.
    """
    if isotope.symbol == 'K' and isotope.mass_number == 40:
        reference_conc = reference.ref_concentration[0]
        reference_conc_unc = reference.ref_concentration_error[0]
        conversion = reference.conversion[0]
    elif isotope.symbol == 'Bi' and isotope.mass_number == 214:
            reference_conc = reference.ref_concentration[1]
            reference_conc_unc = reference.ref_concentration_error[1]
            conversion = reference.conversion[1]
    elif isotope.symbol == 'Pb':
        if isotope.mass_number == 214:
            reference_conc = reference.ref_concentration[2]
            reference_conc_unc = reference.ref_concentration_error[2]
            conversion = reference.conversion[1]
        else:
            reference_conc = reference.ref_concentration[6]
            reference_conc_unc = reference.ref_concentration_error[6]
            conversion = reference.conversion[2]
    elif isotope.symbol == 'Th' and isotope.mass_number == 234:
        reference_conc = reference.ref_concentration[3]
        reference_conc_unc = reference.ref_concentration_error[3]
        conversion = reference.conversion[1]
    elif isotope.symbol == 'Tl' and isotope.mass_number == 208:
        reference_conc = reference.ref_concentration[4]
        reference_conc_unc = reference.ref_concentration_error[4]
        conversion = reference.conversion[2]
    elif isotope.symbol == 'Ac' and isotope.mass_number == 228:
        reference_conc = reference.ref_concentration[5]
        reference_conc_unc = reference.ref_concentration_error[5]
        conversion = reference.conversion[2]
    else:
        reference_conc = 1
        reference_conc_unc = 0
        conversion = 1
    not_in_dirt = ['Cs134', 'Cs137', 'Co60', 'Pb210']
    ref_specific_activity = reference_activity[0] / reference.mass
    if isotope.symbol + str(isotope.mass_number) in not_in_dirt:
        ref_conc_specact_ratio = 1
    else:
        ref_conc_specact_ratio = reference_conc / ref_specific_activity
    error_factor = ((sample_activity[1] / sample_activity[0])**2 +
                    (reference_activity[1] / reference_activity[0])**2 +
                    (reference_conc_unc / reference_conc)**2)
    sample_factor = sample_activity[0] * ref_conc_specact_ratio
    sample_concentration = sample_factor * conversion
    sample_concentration_uncertainty = ((sample_concentration)**2 *
                                        (error_factor))**0.5
    results = [sample_concentration, sample_concentration_uncertainty]
    return results


def peak_finder(spectrum, energy):
    '''
    PEAK_FINDER will search for peaks within a certain range determined by the
    Energy given. It takes a Spectra file and an Energy value as input. The
    energy range to look in is given by the Full-Width-Half-Maximum (FWHM).
    If more than one peak is found in the given range, the peak with the
    highest amount of counts will be used.
    '''
    e0 = spectrum.energy_cal[0]
    eslope = spectrum.energy_cal[1]
    energy_axis = e0 + eslope*spectrum.channel

    peak_energy = []
    # rough estimate of fwhm.
    fwhm = 0.05*energy**0.5
    fwhm_range = 1

    # peak search area
    start_region = np.flatnonzero(energy_axis > energy - fwhm_range * fwhm)[0]
    end_region = np.flatnonzero(energy_axis > energy + fwhm_range * fwhm)[0]
    y = spectrum.data[start_region:end_region]
    indexes = peakutils.indexes(y, thres=0.5, min_dist=4)
    tallest_peak = []
    if indexes.size == 0:
        peak_energy.append(int((end_region - start_region) / 2) + start_region)
    else:
        for i in range(indexes.size):
            spot = spectrum.data[indexes[i]+start_region]
            tallest_peak.append(spot)
        indexes = indexes[np.argmax(tallest_peak)]
        peak_energy.append(int(indexes+start_region))
    peak_energy = float(energy_axis[peak_energy])
    return(peak_energy)


def peak_measurement(M, energy, sub_regions='both'):
    """
    Takes in a measured spectra alongside a specific energy and returns the net
    area and uncertainty for that energy.
    """
    E0 = M.energy_cal[0]
    Eslope = M.energy_cal[1]
    M_counts = M.data
    energy_channel = int((energy - E0) / Eslope)

    region_size = 1.3
    compton_distance = 4
    # Rough estimate of FWHM.
    fwhm = 0.05*energy**0.5
    fwhm_channel = int(region_size * (fwhm - E0) / Eslope)
    # peak gross area
    gross_counts_peak = sum(M_counts[(energy_channel - fwhm_channel):
                                     (energy_channel + fwhm_channel)])

    # Left Gross Area
    left_peak = energy_channel - compton_distance * fwhm_channel
    gross_counts_left = sum(M_counts[(left_peak - fwhm_channel):
                                     (left_peak + fwhm_channel)])
    # Right Gross Area
    right_peak = energy_channel + compton_distance * fwhm_channel
    gross_counts_right = sum(M_counts[(right_peak - fwhm_channel):
                                      (right_peak + fwhm_channel)])
    compton_region = [gross_counts_left, gross_counts_right]

    if sub_regions == 'left':
        compton_region = [compton_region[0]]
    elif sub_regions == 'right':
        compton_region = [compton_region[1]]
    elif sub_regions == 'none':
        compton_region = [0, 0]
    # Net Area
    net_area = gross_counts_peak - np.mean(compton_region)
    # Uncertainty - 2-sigma
    gross_area_uncertainty = (gross_counts_peak)**0.5
    if len(compton_region) < 2:
        compton_region_uncertainty = (compton_region[0])**0.5
    else:
        compton_region_uncertainty = (compton_region[0] +
                                      compton_region[1])**0.5
    uncertainty = 2 * (gross_area_uncertainty**2 +
                       compton_region_uncertainty**2)**0.5
    # Returning results
    results = [net_area, uncertainty]
    return results


def background_subtract(meas_area, back_area, meas_time, back_time):
    """
    Background_Subtract will subtract a measured Background peak net area from
    a sample peak net area. The background peak is converted to the same time
    scale as the measurement and the subtraction is performed. All inputs are
    scalar numbers, where Meas_Area and Back_Area represent the net area of
    a sample net area and background net area respectively. Meas_Time and
    Back_Time are the livetimes of the measurement and background respectively.
    """

    time_ratio = meas_time / back_time
    back_to_meas = back_area[0] * time_ratio
    meas_sub_back = meas_area[0] - back_to_meas

    meas_uncertainty = meas_area[1]
    back_uncertainty = back_area[1] * time_ratio
    meas_sub_back_uncertainty = (meas_uncertainty**2 +
                                 back_uncertainty**2)**0.5

    sub_peak = [meas_sub_back, meas_sub_back_uncertainty]
    return sub_peak


def make_table(isotope_list, sample_info, sample_names, dates):
    data = {}
    df = pd.read_csv('RadWatch_Samples.csv')
    mass = pd.Series.tolist(df.ix[:, 2])
    for j in range(len(mass)):
        if np.isnan(mass[j]):
            mass[j] = 1
        else:
            mass[j] = float(mass[j])
        mass[j] = 1000/mass[j]
    for i in range(len(sample_names)):
        value = np.array(sample_info[i]) * mass[i]
        data[sample_names[i]] = np.array(value.round(decimals=2))

    isotope_act_unc = []
    for i in range(len(isotope_list)):
        isotope_act_unc.append(str(isotope_list[i].symbol) + '-' +
                               str(isotope_list[i].mass_number) +
                               ' Act' + '[Bq/kg]')
        isotope_act_unc.append(str(isotope_list[i].symbol) + '-' +
                               str(isotope_list[i].mass_number) +
                               ' Unc' + '[Bq/kg]')

    frame = pd.DataFrame(data, index=isotope_act_unc)
    frame = frame.T
    frame.index.name = 'Sample Type'
    # Adding Date Measured and Sample Weight Columns

    frame['Date Measured'] = dates
    frame['Sample Weight (g)'] = pd.Series.tolist(df.ix[:, 2])

    # Reindexing columns to place 'Date Measured' and 'Sample Weight' first.
    colnames = frame.columns.tolist()
    colnames = colnames[-2:] + colnames[:-2]
    frame = frame[colnames]
    frame.to_csv('Sampling_Table.csv')
    return frame


def acquire_files():
    """
    acquire_files gathers all the .Spe file in the current file directory and
    returns a list containing all .Spe files.
    """
    sample_measurements = []
    sample_names = []
    dir_path = os.getcwd()
    for file in os.listdir(dir_path):
        if file.lower().endswith(".spe"):
            "Ignore the background and reference spectra"
            if file == "USS_Independence_Background.Spe":
                pass
            elif file == "UCB018_Soil_Sample010_2.Spe":
                pass
            else:
                sample_measurements.append(file)
                name = os.path.splitext(file)[0].replace("_", " ")
                sample_names.append(str(name))
    return sample_measurements, sample_names


def main():
    background = SPEFile.SPEFile("USS_Independence_Background.Spe")
    background.read()
    reference = SPEFile.SPEFile("UCB018_Soil_Sample010_2.Spe")
    reference.read()
    sample_comparison = ref.soil_reference
    sample_measurements, sample_names = acquire_files()
    measurement_dates = []
    sample_data = []
    error_spectrum = []

    for sample in sample_measurements:
        measurement = SPEFile.SPEFile(sample)
        measurement.read()
        measurement_dates.append(measurement.collection_start.split(' ')[0])
        check_energies = [1120.29, 1460.83, 1764.49, 2614.51]
        for energy in check_energies:
                background_energy = peak_finder(background, energy)
                background_peak = peak_measurement(background,
                                                   background_energy)
                sample_energy = peak_finder(measurement, energy)
                sample_net_area = peak_measurement(measurement, sample_energy)
                check = background_subtract(sample_net_area,
                                            background_peak,
                                            measurement.livetime,
                                            background.livetime)
                if check[0] < 0:
                    significance = check[0]/check[1]
                    if significance < -1:
                        error_spectrum.append(sample)
                        break
        isotope_list = [ii.potassium_40, ii.bismuth_214, ii.thallium_208,
                        ii.caesium_137, ii.caesium_134, ii.cobalt_60,
                        ii.actinium_228, ii.lead_212, ii.lead_214,
                        ii.thorium_234, ii.lead_210]
        activity_info = []
        for isotope in isotope_list:
            if isotope.symbol == 'Cs' and isotope.mass_number == 134:
                compton_region = 'left'
            else:
                compton_region = 'both'
            isotope_efficiency = absolute_efficiency(isotope.list_sig_g_e)
            isotope_energy = isotope.list_sig_g_e
            gamma_emission = []
            gamma_uncertainty = []
            ref_emission = []
            ref_uncertainty = []

            for j in range(len(isotope_energy)):
                background_energy = peak_finder(background, isotope_energy[j])
                background_peak = peak_measurement(background,
                                                   background_energy,
                                                   compton_region)
                sample_energy = peak_finder(measurement, isotope_energy[j])
                sample_net_area = peak_measurement(measurement, sample_energy,
                                                   compton_region)
                reference_energy = peak_finder(reference, isotope_energy[j])
                reference_peak = peak_measurement(reference, reference_energy,
                                                  compton_region)
                net_area = background_subtract(sample_net_area,
                                               background_peak,
                                               measurement.livetime,
                                               background.livetime)
                peak_emission = emission_rate(net_area, isotope_efficiency[j],
                                              measurement.livetime)
                reference_area = background_subtract(reference_peak,
                                                     background_peak,
                                                     reference.livetime,
                                                     background.livetime)
                reference_emission = emission_rate(reference_area,
                                                   isotope_efficiency[j],
                                                   reference.livetime)
                gamma_emission.append(peak_emission[0])
                gamma_uncertainty.append(peak_emission[1])
                ref_emission.append(reference_emission[0])
                ref_uncertainty.append(reference_emission[1])
            activity = isotope_activity(isotope, gamma_emission,
                                        gamma_uncertainty)
            reference_activity = isotope_activity(isotope,
                                                  ref_emission,
                                                  ref_uncertainty)
            concentration = isotope_concentration(isotope, sample_comparison,
                                                  activity, reference_activity)
            activity_info.extend(concentration)
        sample_data.append(activity_info)
    if error_spectrum == []:
        pass
    else:
        with open('Error.txt', 'w') as file:
            file.writelines('There is a bias in %s \n' % bias for bias in
                            error_spectrum)
    make_table(isotope_list, sample_data, sample_names, measurement_dates)

if __name__ == '__main__':
    main()
