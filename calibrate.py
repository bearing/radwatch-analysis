import numpy as np
import peakutils
import shutil as sh
import fileinput
import SPEFile
import os


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
    Energy_Axis = E0 + Eslope*spectrum.channel

    Peak_Channel = []
    Found_Energy = []
    Energy_List = [351.93, 583.19, 609.31, 911.20, 1120.29, 1460.82, 1764.49,
                   2614.51]
    skip = 0
    Fix = 0
    for Energy in Energy_List:
        # Rough estimate of FWHM.
        FWHM = 0.05*Energy**0.5
        Range = 0.015*Energy

        # Peak Gross Area

        start_region = np.flatnonzero(Energy_Axis > Energy - Range)[0]

        end_region = np.flatnonzero(Energy_Axis > Energy + Range)[0]
        y = spectrum.data[start_region:end_region]
        indexes = peakutils.indexes(y, thres=0.5, min_dist=4)
        Tallest_Peak = []
        if indexes.size == 0:
            print('Peak Not Found')
            skip += 1
        else:
            for i in range(indexes.size):
                Spot = spectrum.data[indexes[i]+start_region]
                Tallest_Peak.append(Spot)
            indexes = indexes[np.argmax(Tallest_Peak)]
            Peak_Channel.append(int(indexes+start_region))
            Found_Energy.append(Energy)
            Difference = abs((Energy -
                              float(Energy_Axis[int(indexes+start_region)])))
            if Difference > 0.5*FWHM:
                Fix += 1
    if skip > 4:
        Message = 'Error'
    elif Fix >= 4:
        Message = 'Fix'
    else:
        Message = 'Fine'
    return(Peak_Channel, Found_Energy, Message)


def calibration_correction(file_name, measurement, channel, energy):
    """
    calibration_correction implements a corrected energy calibration based
    on the array of channels and energies given as input. It performs a
    least squares regression fit of the channels and energies and implements
    the new energy calibration in a newly generated .Spe file. The new
    spectra file will contain the same information with only the old
    calibration changed.
    """
    Old_Cal = (str(float(measurement.energy_cal[0])) + ' ' +
               str(float(measurement.energy_cal[1])))

    A_matrix = np.vstack([channel, np.ones(len(channel))]).T
    Calibration_Line = np.linalg.lstsq(A_matrix, energy)

    E0 = float(Calibration_Line[0][1])
    Eslope = float(Calibration_Line[0][0])
    New_Cal = str(float(E0)) + ' ' + str(float(Eslope))
    with fileinput.FileInput(file_name, inplace=1) as file:
        for line in file:
            print(line.replace(Old_Cal, New_Cal).rstrip())


def main():
    Sample_Measurements = []
    Cal_Error = []
    dir_path = os.getcwd()
    for file in os.listdir(dir_path):
        if file.endswith(".Spe"):
            if file == "USS_Independence_Background.Spe":
                pass
            else:
                Sample_Measurements.append(file)
    for SAMPLE in Sample_Measurements:
        Measurement = SPEFile.SPEFile(SAMPLE)
        Measurement.read()
        [Channel, Energy, Status] = calibration_check(Measurement)
        if Status == 'Fix':
            if '_recal.Spe' in SAMPLE:
                Cal_Error.append(SAMPLE.replace('_recal.Spe', '.Spe'))
                pass
            else:
                print(('\nFixing calibration for %s \n' % SAMPLE))
                Cal_File = sh.copyfile(SAMPLE, os.path.splitext(SAMPLE)[0] +
                                       '_recal.Spe')
                Fix_Measurement = SPEFile.SPEFile(Cal_File)
                Fix_Measurement.read()
                calibration_correction(Cal_File, Fix_Measurement, Channel,
                                       Energy)
        elif Status == 'Error':
            Cal_Error.append(SAMPLE)
    if Cal_Error == []:
        pass
    else:
        with open('Error_Cal.txt', 'w') as file:
            file.writelines('Check calibration in %s \n' % error for error in
                            Cal_Error)


if __name__ == '__main__':
    main()
