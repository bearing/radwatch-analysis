import numpy as np
import peakutils
import shutil as sh
import fileinput
import SPEFile
import os


def acquire_files():
    """
    acquire_files gathers all the .Spe file in the current file directory and
    returns a list containing all .Spe files.
    """
    sample_measurements = []
    dir_path = os.getcwd()
    for file in os.listdir(dir_path):
        if file.endswith(".Spe"):
            if file == "USS_Independence_Background.Spe":
                pass
            else:
                sample_measurements.append(file)
    return sample_measurements


def peak_offsets(spectrum):
    offset = []
    peak_channel = []
    energy_list = [351.93, 583.19, 609.31, 911.20, 1120.29, 1460.82, 1764.49,
                   2614.51]
    E0 = spectrum.energy_cal[0]
    Eslope = spectrum.energy_cal[1]
    energy_axis = E0 + Eslope*spectrum.channel
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
            offset.append(np.nan)
            peak_channel.append(np.nan)
        else:
            for i in range(indexes.size):
                spot = spectrum.data[indexes[i]+start_region]
                tallest_peak.append(spot)
            indexes = indexes[np.argmax(tallest_peak)]
            difference = ((energy -
                              float(energy_axis[int(indexes+start_region)])))
            offset.append(difference)
            peak_channel.append(int(indexes + start_region))
    return offset, peak_channel


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

    peak_channel = []
    found_energy = []
    energy_list = [351.93, 583.19, 609.31, 911.20, 1120.29, 1460.82, 1764.49,
                   2614.51]
    skip = 0
    fix = 0
    offsets = peak_offsets(spectrum)
    difference = offsets[0]
    channels = offsets[1]
    for i in range(len(difference)):
        fwhm = 0.05 * energy_list[i]**0.5
        if np.isnan(difference[i]):
            skip += 1
        if abs(difference[i]) > 0.5 * fwhm:
            fix += 1
            peak_channel.append(channels[i])
            found_energy.append(energy_list[i])
    if skip > 4:
        message = 'error'
    elif fix >= 4:
        message = 'fix'
    else:
        message = 'fine'
    return(peak_channel, found_energy, message)


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


def main():
    sample_measurements = acquire_files()
    cal_error = []
    double_check = []

    for sample in sample_measurements:
        if '_recal.spe' in sample:
            double_check.append(sample)
            pass
        else:
            measurement = SPEFile.SPEFile(sample)
            measurement.read()
            [channel, energy, status] = calibration_check(measurement)
            if status == 'fix':
                print(('\nFixing calibration for %s \n' % sample))
                cal_file = calibration_correction(sample, channel,
                                                  energy)
                double_check.append(cal_file)
            elif status == 'error':
                cal_error.append(sample)
    for check in double_check:
        Recal = SPEFile.SPEFile(check)
        Recal.read()
        status = calibration_check(Recal)[2]
        if status == 'Fix':
            cal_error.append(check.replace('_recal.Spe', '.Spe'))
    if cal_error == []:
        pass
    else:
        with open('Error_Cal.txt', 'w') as file:
            file.writelines('Check calibration in %s \n' % error for error in
                            cal_error)


if __name__ == '__main__':
    main()
