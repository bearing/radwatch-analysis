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
    Branching_ratio = isotope.list_sig_g_b_r
    Activity = []
    Uncertainty = []
    for i in range(len(Branching_ratio)):
        Activity.append(emission_rates[i]/Branching_ratio[i])
        Uncertainty.append(emission_uncertainty[i]/Branching_ratio[i])
    Isotope_Activity = np.mean(Activity)
    Activity_uncertainty = np.mean(Uncertainty)
    results = [Isotope_Activity, Activity_uncertainty]
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
    if isotope.Symbol == 'K' and isotope.Mass_number == 40:
        Reference_Conc = reference.Ref_Concentration[0]
        Reference_Conc_Unc = reference.Ref_Concentration_Error[0]
        Conversion = reference.Conversion[0]
    elif isotope.Symbol == 'Bi' and isotope.Mass_number == 214:
            Reference_Conc = reference.Ref_Concentration[1]
            Reference_Conc_Unc = reference.Ref_Concentration_Error[1]
            Conversion = reference.Conversion[1]
    elif isotope.Symbol == 'Pb':
        if isotope.Mass_number == 214:
            Reference_Conc = reference.Ref_Concentration[2]
            Reference_Conc_Unc = reference.Ref_Concentration_Error[2]
            Conversion = reference.Conversion[1]
        else:
            Reference_Conc = reference.Ref_Concentration[6]
            Reference_Conc_Unc = reference.Ref_Concentration_Error[6]
            Conversion = reference.Conversion[2]
    elif isotope.Symbol == 'Th' and isotope.Mass_number == 234:
        Reference_Conc = reference.Ref_Concentration[3]
        Reference_Conc_Unc = reference.Ref_Concentration_Error[3]
        Conversion = reference.Conversion[1]
    elif isotope.Symbol == 'Tl' and isotope.Mass_number == 208:
        Reference_Conc = reference.Ref_Concentration[4]
        Reference_Conc_Unc = reference.Ref_Concentration_Error[4]
        Conversion = reference.Conversion[2]
    elif isotope.Symbol == 'Ac' and isotope.Mass_number == 228:
        Reference_Conc = reference.Ref_Concentration[5]
        Reference_Conc_Unc = reference.Ref_Concentration_Error[5]
        Conversion = reference.Conversion[2]
    else:
        Reference_Conc = 1
        Reference_Conc_Unc = 0
        Conversion = 1
    Ref_Specific_Activity = reference_activity[0] / reference.Mass
    Ref_Conc_SpecAct_Ratio = Reference_Conc / Ref_Specific_Activity
    Error_Factor = ((sample_activity[1] / sample_activity[0])**2 +
                    (reference_activity[1] / reference_activity[0])**2 +
                    (Reference_Conc_Unc / Reference_Conc)**2)**0.5
    Sample_Factor = sample_activity[0] * Ref_Conc_SpecAct_Ratio
    Sample_Factor_Uncertainty = Sample_Factor * Error_Factor
    Sample_Concentration = Sample_Factor * Conversion
    Sample_Concentration_Uncertainty = Sample_Factor_Uncertainty * Conversion
    Results = [Sample_Concentration, Sample_Concentration_Uncertainty]
    return Results


def peak_finder(spectrum, energy):
    '''
    PEAK_FINDER will search for peaks within a certain range determined by the
    Energy given. It takes a Spectra file and an Energy value as input. The
    energy range to look in is given by the Full-Width-Half-Maximum (FWHM).
    If more than one peak is found in the given range, the peak with the
    highest amount of counts will be used.
    '''
    E0 = spectrum.energy_cal[0]
    Eslope = spectrum.energy_cal[1]
    Energy_Axis = E0 + Eslope*spectrum.channel

    Peak_Energy = []
    # Rough estimate of FWHM.
    FWHM = 0.05*energy**0.5

    # Peak Gross Area

    start_region = np.flatnonzero(Energy_Axis > energy - 3*FWHM)[0]

    end_region = np.flatnonzero(Energy_Axis > energy + 3*FWHM)[0]
    y = spectrum.data[start_region:end_region]
    indexes = peakutils.indexes(y, thres=0.5, min_dist=4)
    Tallest_Peak = []
    if indexes.size == 0:
        Peak_Energy.append(int((end_region-start_region)/2)+start_region)
    else:
        for i in range(indexes.size):
            Spot = spectrum.data[indexes[i]+start_region]
            Tallest_Peak.append(Spot)
        indexes = indexes[np.argmax(Tallest_Peak)]
        Peak_Energy.append(int(indexes+start_region))
    Peak_Energy = float(Energy_Axis[Peak_Energy])
    return(Peak_Energy)


def peak_measurement(M, energy):
    """
    Takes in a measured spectra alongside a specific energy and returns the net
    area and uncertainty for that energy.
    """
    E0 = M.energy_cal[0]
    Eslope = M.energy_cal[1]
    energy_axis = E0 + Eslope*M.channel
    M_counts = M.data

    # Rough estimate of FWHM.
    FWHM = 0.05*energy**0.5
    # Peak Gross Area
    start_peak = np.flatnonzero(energy_axis > energy - FWHM)[0]
    end_peak = np.flatnonzero(energy_axis > energy + FWHM)[0]
    gross_counts_peak = sum(M_counts[start_peak:end_peak])

    # Left Gross Area
    left_peak = energy - 2*FWHM
    left_start = np.flatnonzero(energy_axis > left_peak - FWHM)[0]
    left_end = np.flatnonzero(energy_axis > left_peak + FWHM)[0]
    gross_counts_left = sum(M_counts[left_start:left_end])

    # Right Gross Area
    right_peak = energy + 2*FWHM
    right_start = np.flatnonzero(energy_axis > right_peak - FWHM)[0]
    right_end = np.flatnonzero(energy_axis > right_peak + FWHM)[0]
    gross_counts_right = sum(M_counts[right_start:right_end])

    # Net Area
    net_area = gross_counts_peak - (gross_counts_left + gross_counts_right)/2
    # Uncertainty
    uncertainty = abs((gross_counts_peak +
                      (gross_counts_left + gross_counts_right) / 4)) ** 0.5
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

    Time_Ratio = meas_time/back_time
    Back_to_Meas = back_area[0]*Time_Ratio
    Meas_Sub_Back = meas_area[0] - Back_to_Meas

    Meas_Uncertainty = meas_area[1]
    Back_Uncertainty = back_area[1]*Time_Ratio
    Meas_Sub_Back_Uncertainty = (Meas_Uncertainty+Back_Uncertainty)**0.5

    Sub_Peak = [Meas_Sub_Back, Meas_Sub_Back_Uncertainty]
    return Sub_Peak


def make_table(isotope_List, sample_info, sample_names, dates):
    data = {}

    for i in range(len(sample_names)):
        data[sample_names[i]] = sample_info[i]

    Isotope_Act_Unc = []
    for i in range(len(isotope_List)):
        Isotope_Act_Unc.append(str(isotope_List[i].Symbol) + '-' +
                               str(isotope_List[i].Mass_number) +
                               ' Act' + '[Bq]')
        Isotope_Act_Unc.append(str(isotope_List[i].Symbol) + '-' +
                               str(isotope_List[i].Mass_number) +
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
    Background = SPEFile.SPEFile("USS_Independence_Background.Spe")
    Background.read()
    Reference = SPEFile.SPEFile("UCB018_Soil_Sample010_2.Spe")
    Reference.read()
    Sample_Comparison = ref.Soil_Reference
    dir_path = os.getcwd()
    Sample_Measurements = []
    SAMPLE_NAMES = []
    Measurement_Dates = []
    Sample_Data = []
    Error_Spectrum = []

    for file in os.listdir(dir_path):
        if file.endswith(".Spe"):
            if file == "USS_Independence_Background.Spe":
                pass
            else:
                Sample_Measurements.append(file)
                Name = os.path.splitext(file)[0].replace("_", " ")
                SAMPLE_NAMES.append(Name)

    for SAMPLE in Sample_Measurements:
        Measurement = SPEFile.SPEFile(SAMPLE)
        Measurement.read()
        Measurement_Dates.append(Measurement.collection_start.split(' ')[0])
        Check_Energies = [1120.29, 1460.83, 1764.49, 2614.51]
        for energy in Check_Energies:
                Background_Energy = peak_finder(Background, energy)
                Background_Peak = peak_measurement(Background,
                                                   Background_Energy)
                Sample_Energy = peak_finder(Measurement, energy)
                Sample_Net_Area = peak_measurement(Measurement, Sample_Energy)
                Check = background_subtract(Sample_Net_Area,
                                            Background_Peak,
                                            Measurement.livetime,
                                            Background.livetime)
                if Check[0] < 0:
                    Significance = Check[0]/Check[1]
                    if Significance < -2:
                        Error_Spectrum.append(SAMPLE)
                        break
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
            Ref_Emission = []
            Ref_Uncertainty = []

            for j in range(len(Isotope_Energy)):
                Background_Energy = peak_finder(Background, Isotope_Energy[j])
                Background_Peak = peak_measurement(Background,
                                                   Background_Energy)
                Sample_Energy = peak_finder(Measurement, Isotope_Energy[j])
                Sample_Net_Area = peak_measurement(Measurement, Sample_Energy)
                Reference_Energy = peak_finder(Reference, Isotope_Energy[j])
                Reference_Peak = peak_measurement(Reference, Reference_Energy)
                Net_Area = background_subtract(Sample_Net_Area,
                                               Background_Peak,
                                               Measurement.livetime,
                                               Background.livetime)

                Peak_emission = emission_rate(Net_Area, Isotope_Efficiency[j],
                                              Measurement.livetime)
                Reference_Area = background_subtract(Reference_Peak,
                                                     Background_Peak,
                                                     Reference.livetime,
                                                     Background.livetime)
                Reference_Emission = emission_rate(Reference_Area,
                                                   Isotope_Efficiency[j],
                                                   Reference.livetime)
                Gamma_Emission.append(Peak_emission[0])
                Gamma_Uncertainty.append(Peak_emission[1])
                Ref_Emission.append(Reference_Emission[0])
                Ref_Uncertainty.append(Reference_Emission[1])
            Activity = isotope_activity(isotope, Gamma_Emission,
                                        Gamma_Uncertainty)
            Reference_Activity = isotope_activity(isotope,
                                                  Ref_Emission,
                                                  Ref_Uncertainty)
            Concentration = isotope_concentration(isotope, Sample_Comparison,
                                                  Activity, Reference_Activity)
            Activity_Info.extend(Concentration)
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
