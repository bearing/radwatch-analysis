import matplotlib.pyplot as plt
import numpy as np
import itertools
import SPEFile
from ROI_Maker import ROI_Maker
import Gamma_Isotopes
from Updated_Peak_Finder import peak_finder_pro

def gamma_plotter(spectrum, energy_range=None, use='spectrum', title_text=None):
    """
    spectrum plotter for Gamma_Analysis.py
    spectrum needs to be a spectrum object.
    """

    # title text
    if title_text is None:
        title_text = spectrum.filename

    # plots the spectrum only.
    counts = spectrum.data
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel * spectrum.channel
    plt.plot(energy_axis, counts)
    plt.title(title_text)

    #highlights peaks of interest.
    if use == 'peaks':

        energies = [Gamma_Isotopes.bismuth_214.list_sig_g_e,
                    Gamma_Isotopes.caesium_134.list_sig_g_e,
                    Gamma_Isotopes.caesium_137.list_sig_g_e,
                    Gamma_Isotopes.potassium_40.list_sig_g_e,
                    Gamma_Isotopes.thallium_208.list_sig_g_e]

        #flattening the energies list.
        energies = list(itertools.chain(*energies))

        for energy in energies:
            peak_ch, side_ch_list = ROI_Maker(spectrum, energy)
            highlgiht(energy_axis, counts, zero_offset, energy_per_channel, peak_ch, facecolor = 'r')
            for side_energy in side_ch_list:
                highlgiht(energy_axis, counts, zero_offset, energy_per_channel, side_energy, facecolor = 'b')

    #rescales linear plot to semilog plot.
    plt.xlim(xmin=0)
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')

    if energy_range is not None:
        plt.xlim([energy_range[0], energy_range[1]])


def highlight(energy_axis, counts, zero_offset, energy_per_channel, channel_list, facecolor):
    left_region = (energy_axis >= zero_offset + energy_per_channel*channel_list[0])
    right_region = (energy_axis <= zero_offset + energy_per_channel*channel_list[1])
    region = left_region & right_region
    plt.fill_between(energy_axis, counts, where=region, facecolor=facecolor)


def naa_plotter(SPE_File_Name, energy_range=None, subregions=None, use='spectrum'):
    """
    spectrum plotter for NAA_Analysis.py
    SPE_File_Name needs to be a string.
    """

    #loading the SPE_File_Name
    spectrum = SPEFile.SPEFile(SPE_File_Name)
    spectrum.read()

    #plots the spectrum only.
    counts = spectrum.data
    zero_offset = spectrum.energy_cal[0]
    energy_per_channel = spectrum.energy_cal[1]
    energy_axis = zero_offset + energy_per_channel*spectrum.channel
    plt.plot(energy_axis, counts)
    plt.title(SPE_File_Name)

    #highlights all peaks.
    if use == 'peaks':

        peak_channels = peak_finder_pro(spectrum)
        peak_energies = zero_offset + float(energy_per_channel)*np.array(peak_channels)
        #[i*energy_per_channel for i in peak_channels]
        for i in range(len(peak_energies)):
            peak_ch, side_ch_list = ROI_Maker(spectrum, peak_energies[i])

            plt.fill_between(energy_axis, counts,
            where=(energy_axis >= zero_offset + energy_per_channel*peak_ch[0]) &
            (energy_axis <= zero_offset + energy_per_channel*peak_ch[1]), facecolor='r')

            #highlights compton regions.
            if subregions == 'both':
                plt.fill_between(energy_axis, counts,
                where=(energy_axis >= zero_offset + energy_per_channel*side_ch_list[0][0]) &
                (energy_axis <= zero_offset + energy_per_channel*side_ch_list[0][1]), facecolor='b')
                plt.fill_between(energy_axis, counts,
                where=(energy_axis >= zero_offset + energy_per_channel*side_ch_list[1][0]) &
                (energy_axis <= zero_offset + energy_per_channel*side_ch_list[1][1]), facecolor='b')

    #rescales linear plot to semilog plot.
    plt.xlim(xmin=0)
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')

    if energy_range is not None:
        plt.xlim([energy_range[0], energy_range[1]])
