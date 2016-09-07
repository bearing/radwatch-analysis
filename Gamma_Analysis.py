"""
This will perform a gamma analysis
It will collect two spectra:
M = Measurement Spectrum
B = Background Spectrum
"""
from __future__ import print_function
from SpectrumFileBase import SpectrumFileBase
import Isotope_identification as ii
import SPEFile
import math
import numpy as np
import matplotlib.pyplot as plt
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
        efficiency.append(math.exp(coeffs[3] *
                          (math.log(energy[i])/energy[i])**3 +
                          coeffs[2]*(math.log(energy[i])/energy[i])**2 +
                          coeffs[1]*(math.log(energy[i])/energy[i]) +
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


def Isotope_Activity(Isotope, emission_rates, emission_uncertainty):
    """
    Isotope_Activity will determine the activity of a given radioactive isotope
    based on the emission rates given and the isotope properties. It takes an
    Isotope object and a given set of emission rates and outputs an activity
    estimate alongside its uncertainty.
    """
    Branching_ratio = Isotope.list_sig_g_b_r
    Activity = []
    Uncertainty = []
    for i in range(len(Branching_ratio)):
        Activity.append(emission_rates[i]/Branching_ratio[i])
        Uncertainty.append(emission_uncertainty[i]/Branching_ratio[i])
    Isotope_Activity = np.mean(Activity)
    Activity_uncertainty = np.mean(Uncertainty)
    results = [Isotope_Activity, Activity_uncertainty]
    return results


def peak_measurement(M, energy):
    """
    Takes in a measured spectra alongside a specific energy and returns the net
    area and uncertainty for that energy.
    """
    energy_axis = M[0]
    M_counts = M[1]

    # Rough estimate of FWHM.
    FWHM = 0.05*energy**0.5

    # Peak Gross Area

    start_peak = 0
    while energy_axis[start_peak] < (energy - FWHM):
        start_peak += 1

    end_peak = start_peak
    while energy_axis[end_peak] < (energy + FWHM):
        end_peak += 1

    gross_counts_peak = sum(M_counts[start_peak:end_peak])

    # Left Gross Area

    left_peak = energy - 2*FWHM

    left_start = 0
    while energy_axis[left_start] < (left_peak - FWHM):
        left_start += 1

    left_end = left_start
    while energy_axis[left_end] < (left_peak + FWHM):
        left_end += 1

    gross_counts_left = sum(M_counts[left_start:left_end])

    # Right Gross Area

    right_peak = energy + 2*FWHM

    right_start = 0
    while energy_axis[right_start] < (right_peak - FWHM):
        right_start += 1

    right_end = right_start
    while energy_axis[right_end] < (right_peak + FWHM):
        right_end += 1

    gross_counts_right = sum(M_counts[right_start:right_end])

    # Net Area

    net_area = gross_counts_peak - (gross_counts_left + gross_counts_right)/2

    # Uncertainty

    uncertainty = abs((gross_counts_peak +
                      (gross_counts_left + gross_counts_right) / 4)) ** 0.5

    # Returning results

    results = [net_area, uncertainty]

    return results


def Background_Subtract(M, B):
    """
    Background_Subtract will subtract the background spectrum
    from a given measurement. This will return the energy bins using a given
    energy calibration as well as the background subtracted counts of a
    measurement. Since both spectra come from the same detector, this assumes
    the energy calibrations are the same.
    """

    M_Counts = M.data
    B_Counts = B.data

    M_Time = M.livetime
    B_Time = B.livetime

    B_Channels = B.channel
    E0 = M.energy_cal[0]
    Eslope = M.energy_cal[1]

    Energy_Axis = M.channel
    channel_ratio = (len(Energy_Axis)+1)/(len(B_Channels)+1)
    if channel_ratio == 1:
        Energy_Axis = Energy_Axis.astype(float)
        Energy_Axis[:] = [E0+Eslope*x for x in B_Channels]
        B_Counts_M = [1.0]*len(M.channel)
        B_Counts_M[:] = [x*(M_Time/B_Time) for x in B_Counts]
        M_Sub_Back = [1.0]*len(B_Channels)
        M_Sub_Back = [M_Counts[x]-B_Counts_M[x] for x in M.channel]
        Sub_Spect = [Energy_Axis, M_Sub_Back]
    else:
        MOD = (len(Energy_Axis)+1) % channel_ratio
        REM = channel_ratio - MOD + 1
        M_Counts = np.append(M_Counts, np.zeros(REM))
        M_Counts = M_Counts.reshape((-1, channel_ratio))
        M_Counts = np.sum(M_Counts, 1)
        Energy_Axis = Energy_Axis.astype(float)
        Energy_Axis[:] = [E0+Eslope*x for x in M.channel]
        Energy_Axis = np.append(Energy_Axis, np.zeros(REM))
        Energy_Axis = Energy_Axis.reshape((-1, channel_ratio))
        Energy_Axis = np.mean(Energy_Axis, 1)
        B_Counts_M = [1.0]*len(B.channel)
        B_Counts_M[:] = [x*(M_Time/B_Time) for x in B_Counts]
        M_Sub_Back = [1.0]*len(M_Counts)
        M_Sub_Back = [M_Counts[x]-B_Counts_M[x] for x in B.channel]
        Sub_Spect = [Energy_Axis, M_Sub_Back]
    return Sub_Spect


def Bias_Check(Spectrum, Background, Measurement_Name):
    """
    Bias_Check will determine if there's a bias in the measurement. It will
    look at high energy peaks that correspond to Bi-214 and Tl-208 since these
    peaks occur in the background. If the net area of those peaks are negative
    beyond 2 sigma, where sigma is the uncertainty of a peak net area, then a
    message indicating a measurement bias will be produced.
    """
    Check_Energies = [1120.29, 1764.49, 2614.51]
    Message = "FINE"
    M_Counts = Spectrum.data
    B_Counts = Background.data

    M_Time = Spectrum.livetime
    B_Time = Background.livetime
    Time_Ratio = M_Time/B_Time

    B_Channels = Background.channel
    E0 = Spectrum.energy_cal[0]
    Eslope = Spectrum.energy_cal[1]

    Energy_Axis = Spectrum.channel
    channel_ratio = (len(Energy_Axis)+1)/(len(B_Channels)+1)
    if channel_ratio == 1:
        Energy_Axis = Energy_Axis.astype(float)
        Energy_Axis[:] = [E0+Eslope*x for x in B_Channels]
    else:
        MOD = (len(Energy_Axis)+1) % channel_ratio
        REM = channel_ratio - MOD + 1
        M_Counts = np.append(M_Counts, np.zeros(REM))
        M_Counts = M_Counts.reshape((-1, channel_ratio))
        M_Counts = np.sum(M_Counts, 1)
        Energy_Axis = Energy_Axis.astype(float)
        Energy_Axis[:] = [E0+Eslope*x for x in Spectrum.channel]
        Energy_Axis = np.append(Energy_Axis, np.zeros(REM))
        Energy_Axis = Energy_Axis.reshape((-1, channel_ratio))
        Energy_Axis = np.mean(Energy_Axis, 1)

    for energy in Check_Energies:
        FWHM = 0.05*energy**0.5
        start_peak = 0
        while Energy_Axis[start_peak] < (energy - FWHM):
            start_peak += 1

        end_peak = start_peak
        while Energy_Axis[end_peak] < (energy + FWHM):
            end_peak += 1
        Peak_Area = sum(M_Counts[start_peak:end_peak])
        Peak_Area_Uncertainty = (Peak_Area)**0.5

        Background_Area = sum(B_Counts[start_peak:end_peak])
        Background_Uncertainty = (Background_Area)**0.5

        B_to_M_Area = Background_Area*Time_Ratio
        B_to_M_Uncertainty = Background_Uncertainty*Time_Ratio

        Check_Area = Peak_Area - B_to_M_Area
        Check_Area_Uncertainty = (Peak_Area_Uncertainty +
                                  B_to_M_Uncertainty)**0.5
        if Check_Area < 0:
            Significance = Check_Area/Check_Area_Uncertainty
            if Significance < -2:
                Message = 'BIAS'
    return(Message)


def make_table(Isotope_List, sample_info, sample_names, dates):
    data = {}

    for i in range(len(sample_names)):
        data[sample_names[i]] = sample_info[i]

    Isotope_Act_Unc = []
    for i in range(len(Isotope_List)):
        Isotope_Act_Unc.append(str(Isotope_List[i].Symbol) + '-' +
                               str(Isotope_List[i].Mass_number) +
                               ' Act' + '[Bq]')
        Isotope_Act_Unc.append(str(Isotope_List[i].Symbol) + '-' +
                               str(Isotope_List[i].Mass_number) +
                               ' Unc' + '[Bq]')

    frame = pd.DataFrame(data, index=Isotope_Act_Unc)
    frame = frame.T
    frame.index.name = 'Sample Type'

    #Adding Date Measured and Sample Weight Columns
    df = pd.read_csv('RadWatch_Samples.csv')
    frame['Date Measured'] = dates
    frame['Sample Weight (g)'] = pd.Series.tolist(df.ix[:,2])

    #Reindexing columns to place 'Date Measured' and 'Sample Weight' first.
    colnames = frame.columns.tolist()
    colnames = colnames[-2:] + colnames[:-2]
    frame = frame[colnames]
    frame.to_csv('Sampling_Table.csv')

    return frame


def main():
    Background = SPEFile.SPEFile("Background_Measurement.Spe")
    Background.read()
    dir_path = os.getcwd()
    Sample_Measurements = []
    SAMPLE_NAMES = []
    Measurement_Dates = []
    Sample_Data = []
    Error_Spectrum = []

    for file in os.listdir(dir_path):
        if file.endswith(".Spe"):
            if file == "Background_Measurement.Spe":
                pass
            else:
                Sample_Measurements.append(file)
                Name = os.path.splitext(file)[0].replace("_", " ")
                SAMPLE_NAMES.append(Name)

    for SAMPLE in Sample_Measurements:
        Measurement = SPEFile.SPEFile(SAMPLE)
        Measurement.read()
        Measurement_Dates.append(Measurement.collection_start.split(' ')[0])
        Check = Bias_Check(Spectrum=Measurement, Background=Background,
                           Measurement_Name=SAMPLE)
        if Check == "BIAS":
            Error_Spectrum.append(SAMPLE)
        Sub_Measurement = Background_Subtract(M=Measurement, B=Background)

        Isotope_List = [ii.Caesium_134, ii.Caesium_137, ii.Cobalt_60,
                        ii.Potassium_40, ii.Thallium_208, ii.Actinium_228,
                        ii.Lead_212, ii.Bismuth_214, ii.Lead_214,
                        ii.Thorium_234, ii.Lead_210]
        Activity_Info = []
        for isotope in Isotope_List:
            Isotope_Efficiency = absolute_efficiency(isotope.list_sig_g_e)
            Isotope_Energy = isotope.list_sig_g_e
            Gamma_Emission = []
            Gamma_Uncertainty = []

            for j in range(len(Isotope_Energy)):
                Net_Area = peak_measurement(Sub_Measurement, Isotope_Energy[j])
                Peak_emission = emission_rate(Net_Area, Isotope_Efficiency[j],
                                              Measurement.livetime)
                Gamma_Emission.append(Peak_emission[0])
                Gamma_Uncertainty.append(Peak_emission[1])
            Activity = Isotope_Activity(isotope, Gamma_Emission,
                                        Gamma_Uncertainty)
            Activity_Info.extend(Activity)
        Sample_Data.append(Activity_Info)
    if Error_Spectrum == []:
        pass
    else:
        with open('Error.txt', 'w') as file:
            file.writelines('There is a bias in %s \n' % bias for bias in
                            Error_Spectrum)
    make_table(Isotope_List, Sample_Data, SAMPLE_NAMES, Measurement_Dates)

if __name__ == '__main__':
    main()
