"""
This will perform a gamma analysis
It will collect two spectra:
M = Measurement Spectrum
B = Background Spectrum
"""
from __future__ import print_function
from SpectrumFileBase import SpectrumFileBase
import SPEFile
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
# exec('Isotope_identification.py')
# Use bottom line for Python 3 only. Use top comment for Python 2.7 only.
exec(open('Isotope_identification.py').read())


EFFICIENCY_CAL_COEFFS = [5.1164, 161.65, 3952.3, 30908]


def absolute_efficiency(energy, coeffs=EFFICIENCY_CAL_COEFFS):
    """
    Returns absolute efficiencies for a given set of energies, based on a
    provided efficiency calibration.
    """
    efficiency = []
    for i in range(len(energy)):
        efficiency.append(math.exp(coeffs[3] *
                          (math.log(energy[i])/energy[i])**3 -
                          coeffs[2]*(math.log(energy[i])/energy[i])**2 +
                          coeffs[1]*(math.log(energy[i])/energy[i]) -
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
    """
    energy_range = M.channel[left_start:right_end]
    for i in energy_range:
        turns = 0
        while turns <= len(energy_range):
            if abs(M_counts[i]) > 2*uncertainty:
                    print("Error: There is a bias in the measurement at %s KeV"
                          % energy_axis[i])
            turns += 1
    """
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

    M_Channels = M.channel
    E0 = M.energy_cal[0]
    Eslope = M.energy_cal[1]

    Energy_Axis = B.channel
    Energy_Axis = Energy_Axis.astype(float)
    Energy_Axis[:] = [E0+Eslope*x for x in M_Channels]

    B_Counts_M = [1.0]*len(M.channel)

    B_Counts_M[:] = [x*(M_Time/B_Time) for x in B_Counts]

    M_Sub_Back = [1.0]*len(M_Channels)

    M_Sub_Back = [M_Counts[x]-B_Counts_M[x] for x in M.channel]

    Sub_Spect = [Energy_Axis, M_Sub_Back]

    return Sub_Spect


def make_table(Isotope_List, sample_info, sample_names):
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
    frame.to_csv('Sampling_Table.csv')


def main():
    Background = SPEFile.SPEFile("Background_Measurement.Spe")
    Background.read()
    dir_path = os.getcwd()
    Sample_Measurements = []
    SAMPLE_NAMES = []
    Sample_Data = []

    for file in os.listdir(dir_path):
        if file.endswith(".Spe"):
            if file == "Background_Measurement.Spe":
                pass
            else:
                Sample_Measurements.append(file)
                Name = os.path.splitext(file)[0].split("_",
                                                       1)[1].replace("_", " ")
                SAMPLE_NAMES.append(Name)

    for SAMPLE in Sample_Measurements:
        Measurement = SPEFile.SPEFile(SAMPLE)
        Measurement.read()

        Sub_Measurement = Background_Subtract(M=Measurement, B=Background)

        Isotope_List = [Caesium_134, Caesium_137, Cobalt_60, Potassium_40,
                        Thallium_208, Actinium_228, Lead_212, Bismuth_214,
                        Lead_214, Thorium_234, Lead_210]
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
    make_table(Isotope_List, Sample_Data, SAMPLE_NAMES)


if __name__ == '__main__':
    main()
