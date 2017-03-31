import numpy as np
import peakutils
from Isotope_identification import Cs_134_g_e

EFFICIENCY_CAL_COEFFS = [-5.1164, 161.65, -3952.3, 30908]

def ROI_Maker(spectrum, energy, sub_regions='auto'):
    """
    Takes in a measured spectrum and identifies peaks by energy.
    Uses peak_finder to localize the peak more precisely from the
    given energy. Also returns peak and compton ROIs as well as each ROIs gross
    area.
    """

    peak_energy = peak_finder(spectrum, energy)

    E0 = spectrum.energy_cal[0]
    Eslope = spectrum.energy_cal[1]
    energy_channel = int((peak_energy - E0) / Eslope)

    region_size = 1.3
    compton_distance = 4

    # Rough estimate of FWHM.
    fwhm = 0.05*peak_energy**0.5
    fwhm_channel = int(region_size * (fwhm - E0) / Eslope)
    # peak gross area
    peak_ch = (energy_channel - fwhm_channel, energy_channel + fwhm_channel)

    left_center = energy_channel - compton_distance * fwhm_channel
    left_ch = (left_center - fwhm_channel, left_center + fwhm_channel)

    right_center = energy_channel + compton_distance * fwhm_channel
    right_ch = (right_center - fwhm_channel, right_center + fwhm_channel)

    if sub_regions == 'auto':
        if energy == Cs_134_g_e[2]:
            sub_regions = 'Cs134'
        else:
            sub_regions = 'both'

    if sub_regions == 'left':
        side_region_list = [left_ch]
    elif sub_regions == 'right':
        side_region_list = [right_ch]
    elif sub_regions == 'Cs134':
        # Cs134 compton region using Bi214 609 peak.
        bi_fwhm = 0.05 * (609.31)**0.5
        bi_fwhm_channel = int(region_size * (bi_fwhm - E0) / Eslope)
        bi_peak_channel = int((609.31 - E0) / Eslope)
        bi_right_peak = bi_peak_channel + compton_distance * bi_fwhm_channel
        bi_right_ch = (bi_right_peak - fwhm_channel,
                       bi_right_peak + fwhm_channel)
        side_region_list = [left_ch, bi_right_ch]
    elif sub_regions == 'none':
        side_region_list = []
    else:
        side_region_list = [left_ch, right_ch]

    return peak_ch, side_region_list


def peak_finder(spectrum, energy):
    '''
    PEAK_FINDER will search for peaks within a certain range determined by the
    Energy given. It takes a spectrum object and an Energy value as input. The
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

def peak_measurement(M, energy, sub_regions='auto'):
    """
    Takes in a measured spectra alongside a specific energy and returns the net
    area and uncertainty (2-sigma) for that energy.
    """

    peak_ch, side_ch_list = ROI_Maker(M, energy, sub_regions=sub_regions)
    gross_area_peak = sum(M.data[peak_ch[0]:peak_ch[1]])
    n_compton = len(side_ch_list)

    if n_compton == 0:
        compton_area = 0
        compton_area_unc = 0
    elif n_compton == 1:
        compton_ch = side_ch_list[0]
        compton_area = M.data[compton_ch[0]:compton_ch[1]]
        compton_area_unc = np.sqrt(compton_area)
    elif n_compton == 2:
        compton_1 = side_ch_list[0]
        compton_2 = side_ch_list[1]
        compton_area_1 = sum(M.data[compton_1[0]:compton_1[1]])
        compton_area_2 = sum(M.data[compton_2[0]:compton_2[1]])
        compton_area = np.mean([compton_area_1, compton_area_2])
        # compton_area_1_unc = sqrt(compton_area_1)
        # propagate uncertainty for taking the mean: /2
        compton_area_unc = np.sqrt(compton_area_1 + compton_area_2) / 2

    net_area = gross_area_peak - compton_area
    net_area_unc = np.sqrt(gross_area_peak + compton_area_unc**2)

    # 2 sigma uncertainty
    return net_area, 2 * net_area_unc

def emission_rate(net_area, efficiency, livetime):
    """
    this function returns the emission rate of gammas per second
    alongside its uncertainty.
    """
    emission_rate = [net_area[0]/(efficiency*livetime),
                     net_area[1]/(efficiency*livetime)]
    return emission_rate

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
    weight = []
    squares_total = []
    for i in range(len(branching_ratio)):
        activity.append(emission_rates[i]/branching_ratio[i])
        uncertainty.append(emission_uncertainty[i]/branching_ratio[i])
        weight.append(1/(emission_uncertainty[i]/branching_ratio[i])**2)
        squares_unc = uncertainty[i]**2 * weight[i]**2
        squares_total.append(squares_unc)
    sum_of_squares = np.sum(squares_total)
    V_1 = np.sum(weight)
    weighted_avg_isotope_activity = np.sum(
        np.array(activity) * np.array(weight)) / V_1
    weighted_avg_isotope_unc = sum_of_squares**0.5 / V_1
    results = [weighted_avg_isotope_activity, weighted_avg_isotope_unc]
    return results