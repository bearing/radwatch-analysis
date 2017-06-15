"""
This will perform a gamma analysis
It will collect two spectra:
M = Measurement Spectrum
B = Background Spectrum
"""
from __future__ import print_function
import Gamma_Isotopes as ii
import Gamma_Reference as ref
import SPEFile
from utils import peak_measurement, emission_rate, isotope_activity
from utils import background_subtract, absolute_efficiency
from calibrate import acquire_files, get_sample_names
import plotter
import numpy as np
import matplotlib.pyplot as plt
import peakutils
import pandas as pd
import os

BACKGROUND = "USS_Independence_Background.Spe"
isotope_list = [ii.potassium_40, ii.bismuth_214, ii.thallium_208,
                ii.caesium_137, ii.caesium_134]


def isotope_concentration(isotope, reference, sample_activity,
                          ref_specific_activity):
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

    if isotope.symbol + str(isotope.mass_number) in not_in_dirt:
        ref_conc_specact_ratio = 1
    else:
        ref_conc_specact_ratio = reference_conc / ref_specific_activity[0]
    error_factor = ((sample_activity[1] / sample_activity[0])**2 +
                    (ref_specific_activity[1] / ref_specific_activity[0])**2 +
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


def make_table(isotope_list, sample_info, sample_names, dates):
    """
    Generate files Sampling_Table.csv and Website_Table.csv
    """
    data = {}
    web_data = {}
    df = pd.read_csv('RadWatch_Samples.csv')
    mass = pd.Series.tolist(df.ix[:, 2])

    for file in sample_names:
        if 'recal' in file:
            sample_names.remove(file)

    print("mass: ", mass)
    print(sample_names)

    if len(mass) != len(sample_names):
        print(
            "\nMetadata in RadWatch_Samples.csv doesn't match the SPE files " +
            "in this directory!\nNot making output CSV's")
        return None
    for j in range(len(mass)):
        if np.isnan(mass[j]):
            mass[j] = 1
        else:
            mass[j] = float(mass[j])
        mass[j] = 1000/mass[j]
    for i in range(len(sample_names)):
        web_value = []
        value = np.array(sample_info[i]) * mass[i]
        for j in range(0, len(value), 2):
            if value[j] <= value[j + 1]:
                web_value.extend(np.array(['N.D.',
                                           value[j + 1].round(decimals=2)]))
            else:
                web_value.extend(np.array([value[j].round(decimals=2),
                                           value[j + 1].round(decimals=2)]))
        data[sample_names[i]] = np.array(value.round(decimals=2))
        web_data[sample_names[i]] = np.array(web_value)
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

    # Saving all acquired results to Sampling_Table.csv file
    frame.to_csv('Sampling_Table.csv')

    web_frame = pd.DataFrame(web_data, index=isotope_act_unc)
    web_frame = web_frame.T
    web_frame.index.name = 'Sample Type'
    # Adding Date Measured and Sample Weight Columns

    web_frame['Date Measured'] = dates
    web_frame['Sample Weight (g)'] = pd.Series.tolist(df.ix[:, 2])

    # Reindexing columns to place 'Date Measured' and 'Sample Weight' first.
    web_frame = web_frame[colnames]
    web_frame.to_csv('Website_Table.csv')

    return frame


def save_peak(sample, energy):
    """
    Plot peak using Spectrum_Peak_Visualization and save into a PNG file.
    """
    cwd = os.getcwd()
    sample_name = os.path.splitext(sample.filename)[0]
    sample_folder = os.path.join(cwd, sample_name)
    # if folder exists, skip next step. Otherwise, create folder for PNGs
    if not os.path.exists(sample_folder):
        try:
            os.makedirs(sample_folder)
        except OSError:
            pass
    label = sample_name + '_' + str(energy) + '_peak'
    fwhm = 0.05 * (energy)**0.5
    energy_range = [(energy - 11 * fwhm), (energy + 11 * fwhm)]
    # generate plot PNG using plotter
    plotter.gamma_plotter(
        sample, energy_range=energy_range, use='peaks', title_text=label)
    PNG_name = label + '.png'
    # move PNGs to newly created folder
    plt.savefig(os.path.join(sample_folder, PNG_name))
    plt.clf()


def analyze_isotope(measurement, background, reference, isotope):
    """
    Calculate concentration for one isotope in one measurement,
    using background spectrum and reference spectrum.
    """

    # ROI sub_regions handled in ROI_Maker.

    isotope_efficiency = absolute_efficiency(isotope.list_sig_g_e)
    isotope_energy = isotope.list_sig_g_e
    gamma_emission = []
    gamma_uncertainty = []

    ref_spec_act = reference.get_spec_activity(isotope, background)

    for j, energy in enumerate(isotope_energy):
        background_peak = peak_measurement(background, energy)
        save_peak(measurement, energy)
        sample_net_area = peak_measurement(measurement, energy)
        fstr = '{}: peak at {:4.0f} keV: {:8.1f} counts +/- {:5.1f} (1-sigma)'
        print(fstr.format(
            measurement.filename,
            energy,
            sample_net_area[0],
            sample_net_area[1] / 2))
        reference_peak = peak_measurement(reference, energy)
        net_area = background_subtract(sample_net_area,
                                       background_peak,
                                       measurement.livetime,
                                       background.livetime)
        peak_emission = emission_rate(net_area, isotope_efficiency[j],
                                      measurement.livetime)

        gamma_emission.append(peak_emission[0])
        gamma_uncertainty.append(peak_emission[1])
    activity = isotope_activity(isotope, gamma_emission,
                                gamma_uncertainty)
    concentration = isotope_concentration(isotope, reference,
                                          activity, ref_spec_act)
    return concentration


def analyze_spectrum(measurement, background, reference):
    """
    Calculate concentrations for isotopes in isotope_list for one spectrum
    using background spectrum and reference spectrum.
    """
    sample_data = []
    for isotope in isotope_list:
        info = analyze_isotope(measurement, background, reference, isotope)
        sample_data.extend(info)
    return sample_data


def check_spectra(samples, background):
    """
    Check for bad calibrations in a list of spectra,
    by seeing if any background peaks in the measurement
    are significantly lower-rate than in the background.
    """
    check_energies = [1120.29, 1460.83, 1764.49, 2614.51]
    error_spectrum = []
    for measurement in samples:
        measurement = SPEFile.SPEFile(measurement)
        measurement.read()
        for energy in check_energies:
                background_peak = peak_measurement(background, energy)
                sample_net_area = peak_measurement(measurement, energy)
                check = background_subtract(sample_net_area,
                                            background_peak,
                                            measurement.livetime,
                                            background.livetime)
                if check[0] < 0:
                    significance = check[0]/check[1]
                    if significance < -1:
                        error_spectrum.append(measurement)
                        print(' * {}: peak at {} less than background'.format(
                            measurement.filename, energy))
                        break
    if error_spectrum == []:
        pass
    else:
        with open('Error.txt', 'w') as file:
            file.writelines('There is a bias in %s \n' % bias for bias in
                            error_spectrum)


def main(background_filename=BACKGROUND, file_list=None):
    background = SPEFile.SPEFile(background_filename)
    background.read()
    if file_list is None:
        sample_measurements, sample_names = acquire_files()
    else:
        sample_measurements = file_list
        sample_names = get_sample_names(sample_measurements)
    print('Got {} spectra'.format(len(sample_names)))
    print('Checking spectra for calibration bias...')
    check_spectra(sample_measurements, background)

    measurement_dates = []
    sample_data = []

    for sample in sample_measurements:

        # Assign the default reference as the S5F reference.
        reference = ref.S5F_reference
        # Assign the Petri reference for samples which utilized that reference.
        for alt_sample in ref.alt_ref_samples:
            if alt_sample in sample:
                reference = ref.petri_reference

        print('Measuring {}...'.format(sample))
        measurement = SPEFile.SPEFile(sample)
        measurement.read()
        measurement_dates.append(measurement.collection_start.split(' ')[0])
        data = analyze_spectrum(measurement, background, reference)
        sample_data.append(data)
    print('Making table...')
    make_table(isotope_list, sample_data, sample_names, measurement_dates)
    print('Finished!')

if __name__ == '__main__':
    main()
