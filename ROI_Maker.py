import numpy as np
import peakutils
from Isotope_identification import Cs_134_g_e
from Isotope_identification import Bi_214_g_e


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

    energy_ch = int((peak_energy - E0) / Eslope)

    region_size = 2.0
    separation_parameter = 1.2

    # Rough estimate of FWHM.
    fwhm_kev = 0.05*peak_energy**0.5
    fwhm_ch = (fwhm_kev - E0)/Eslope

    region_half_width = int(region_size * fwhm_ch)
    region_separation = separation_parameter*fwhm_ch

    peak_ch = (energy_ch - region_half_width, energy_ch + region_half_width)

    left_ch = (energy_ch - region_separation - 3*region_half_width,
               energy_ch - region_separation - region_half_width)

    right_ch = (energy_ch + region_separation + region_half_width,
                energy_ch + region_separation + 3*region_half_width)

    if sub_regions == 'auto':
        if energy == Cs_134_g_e[2]:
            sub_regions = 'Cs134'
        elif energy == Bi_214_g_e[0]:
            sub_regions = 'Bi214'
        else:
            sub_regions = 'both'

    if sub_regions == 'left':
        side_region_list = [left_ch]

    elif sub_regions == 'right':
        side_region_list = [right_ch]

    elif sub_regions == 'Cs134':
        # Cs134 compton region using Bi214 609 peak.
        bi_fwhm_kev = 0.05 * (609.31)**0.5
        bi_fwhm_ch = (bi_fwhm_kev - E0)/Eslope
        bi_region_half_width = int(region_size * bi_fwhm_ch)
        bi_region_separation = separation_parameter*bi_fwhm_ch
        bi_energy_ch = int((609.31 - E0) / Eslope)
        bi_right_ch = (
            bi_energy_ch + bi_region_separation + bi_region_half_width,
            bi_energy_ch + bi_region_separation + 3*bi_region_half_width)
        side_region_list = [left_ch, bi_right_ch]

    elif sub_regions == 'Bi214':
        # Bi214 compton region using Cs134 604 peak.
        cs_fwhm_kev = 0.05 * (604.72)**0.5
        cs_fwhm_ch = (cs_fwhm_kev - E0)/Eslope
        cs_region_half_width = int(region_size*cs_fwhm_ch)
        cs_region_separation = separation_parameter*cs_fwhm_ch
        cs_energy_ch = int((604.72 - E0) / Eslope)
        cs_left_ch = (
            cs_energy_ch - cs_region_separation - 3*cs_region_half_width,
            cs_energy_ch - cs_region_separation - cs_region_half_width)
        side_region_list = [cs_left_ch, right_ch]

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
