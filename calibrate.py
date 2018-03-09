import numpy as np
import peakutils
import pandas as pd
import shutil as sh
import fileinput
import SPEFile
import os

energy_list = [351.93, 583.19, 609.31, 911.20, 1460.82, 1764.49,
               2614.51]
cal_headers = [351.93, 583.19, 609.31, 911.20, 1460.82, 1764.49,
               2614.51, 'Output']


def acquire_files():
    """
    acquire_files gathers all the .Spe files in the current file directory and
    returns a list containing all .Spe files.
    """
    sample_measurements = []
    recal_names = []
    dir_path = os.getcwd()
    for filename in os.listdir(dir_path):
        if filename.lower().endswith(".spe"):
            # Ignore the background and reference spectra
            if filename == "USS_Independence_Background.Spe":
                pass
            elif filename == "UCB018_Soil_Sample010_2.Spe":
                pass
            else:
                if '_recal.spe' in filename.lower():
                    recal_names.append(filename)
                sample_measurements.append(filename)

    sample_measurements.sort()

    print("recal_names: ", recal_names, '\n\n')

    for recal_name in recal_names:
        recal_focus = recal_name.replace('_recal', '')

        if recal_focus in sample_measurements:
            sample_measurements.remove(recal_focus)

    sample_names = get_sample_names(sample_measurements)

    return sample_measurements, sample_names


def calibration_check(spectrum):
    '''
    calibration_check will search for certain peaks that are expected to occur
    in every measured spectra. The energies it searches for are based on peaks
    that occur in background radiation. Once these peaks are found, it
    compares the energy of that peak to the actual energy the peak should be
    at. This check is based on expected detector resolution and if the energy
    deviates to far from the expected value (if beyond half a FWHM), then
    calibration_check sends a message indicating a fix is needed. Only Spectra
    are taken as input.
    '''
    E0 = spectrum.energy_cal[0]
    Eslope = spectrum.energy_cal[1]
    energy_axis = E0 + Eslope*spectrum.channel

    peak_channel = []
    found_energy = []
    offsets = []
    skip = 0
    fix = 0
    for energy in energy_list:
        # rough estimate of fwhm.
        fwhm = 0.05*energy**0.5
        energy_range = 0.015*energy

        # peak gross area

        start_region = np.flatnonzero(energy_axis > energy - energy_range)[0]

        end_region = np.flatnonzero(energy_axis > energy + energy_range)[0]
        y = spectrum.data[start_region:end_region]
        indexes = peakutils.indexes(y, thres=0.5, min_dist=4)
        tallest_peak = []
        if indexes.size == 0:
            print('peak not found')
            offsets.append(np.nan)
            skip += 1
        else:
            for i in range(indexes.size):
                spot = spectrum.data[indexes[i]+start_region]
                tallest_peak.append(spot)
            indexes = indexes[np.argmax(tallest_peak)]
            peak_channel.append(int(indexes+start_region))
            found_energy.append(energy)
            difference = abs((energy -
                              float(energy_axis[int(indexes+start_region)])))
            offsets.append(difference)
            if difference > 0.5*fwhm:
                fix += 1
    if skip > 4:
        message = 'error'
    elif fix >= 4:
        message = 'fix'
    else:
        message = 'fine'
    offsets.append(message)
    return(peak_channel, found_energy, message, offsets)


def calibration_correction(measurement, channel, energy):
    """
    calibration_correction implements a corrected energy calibration based
    on the array of channels and energies given as input. It performs a
    least squares regression fit of the channels and energies and implements
    the new energy calibration in a newly generated .Spe file. The new
    spectra file will contain the same information with only the old
    calibration changed.
    """
    cal_file = sh.copyfile(measurement, os.path.splitext(measurement)[0] +
                           '_recal.Spe')
    fix_measurement = SPEFile.SPEFile(cal_file)
    fix_measurement.read()
    old_cal = (str(float(fix_measurement.energy_cal[0])) + ' ' +
               str(float(fix_measurement.energy_cal[1])))

    a_matrix = np.vstack([channel, np.ones(len(channel))]).T
    calibration_line = np.linalg.lstsq(a_matrix, energy)

    e0 = float(calibration_line[0][1])
    eslope = float(calibration_line[0][0])
    new_cal = str(float(e0)) + ' ' + str(float(eslope))
    with fileinput.FileInput(cal_file, inplace=1) as file:
        for line in file:
            print(line.replace(old_cal, new_cal).rstrip())
    return(cal_file)


def recalibrate(files):
    """

    """
    cal_offsets = []

    for sample in files:
        measurement = SPEFile.SPEFile(sample)
        measurement.read()
        [channel, energy, status, offsets] = calibration_check(measurement)
        cal_offsets.append(offsets)
        if status == 'fix' and '_recal.spe' not in sample.lower():
            print(('\nFixing calibration for %s \n' % sample))
            cal_file = calibration_correction(sample, channel,
                                              energy)
            cal_file_spectrum = SPEFile.SPEFile(cal_file)
            cal_file_spectrum.read()
            cal_check = calibration_check(cal_file_spectrum)[2]
            if cal_check == 'fix':
                print('Spectrum', sample, ' was run through a calibration ',
                      ' correction, but still had a calibration issue.',
                      '\n\n')
        elif status == 'fix' and '_recal.spe' in sample.lower():
            print('Spectrum', sample, ' was recalibrated and still had a ',
                  ' calibration issue.', '\n\n')
        elif status == 'error':
            print('Check calibration for errors in spectrum ', sample)
    calibration_table(files, cal_headers, cal_offsets)


def calibration_table(samples, headers, offsets):

    cal_results = {}
    for i in range(len(samples)):

        cal_results[samples[i]] = np.array(offsets[i])

    cal_frame = pd.DataFrame(cal_results, index=headers)
    cal_frame = cal_frame.T
    cal_frame.index.name = 'Filename'
    cal_frame.to_csv('calibration_results.csv')


def get_sample_names(sample_measurements):
    sample_names = [os.path.splitext(s)[0].replace("_", " ")
                    for s in sample_measurements]
    return sample_names


def main():
    sample_measurements, _ = acquire_files()
    recalibrate(sample_measurements)

if __name__ == '__main__':
    main()
