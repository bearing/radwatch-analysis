import numpy as np
import naa_csv_reader
import naa_csv_maker
import naa_isotope_verifier
import naa_peak_effects
import naa_background
from becquerel.tools import nndc
from pandas import DataFrame
import uncertainties
from itertools import chain
from operator import itemgetter

#def naa_isotope_analyzer(filename):
def naa_isotope_analyzer(energies):
    #runs csv_reader.csv_reader to read the csv file and extract peak energy,
    #net area and uncertainty, and FWHM.
#    csv_data = naa_csv_reader.csv_reader(filename)
#    energies = csv_data['energies']
#    net_area = csv_data['net_area']
#    net_area_unc = csv_data['net_area_unc']
#    peak_cps = csv_data['peak_cps']
#    fwhm = csv_data['fwhm']
#    csv_filename = csv_data['csv_filename']

    #gets rid of 511 keV peak due to annihilation.
    try:
        for i in range(len(energies)):
            if np.isclose(energies[i],511,atol=1) == True:
                energies.remove(energies[i])
#                net_area.remove(net_area[i])
#                net_area_unc.remove(net_area_unc[i])
#                peak_cps.remove(peak_cps[i])
#                fwhm.remove(fwhm[i])
    except:
        pass

    #checks to see if any of the peaks are due to background radiation.
    background_isotopes = []
    background_isotopes_energy = []
    background_isotopes_br = []
    for i in range(len(energies)):
        background_isotopes.append(naa_background.background(energies[i])['identified_isotopes'])
        background_isotopes_energy.append(naa_background.background(energies[i])['identified_isotopes_energy'])
        background_isotopes_br.append(naa_background.background(energies[i])['identified_isotopes_br'])

    #checks to see if any of the peaks are due to single escape peaks,
    #double escape peaks, and sum peaks.
    peak_effects_info = naa_peak_effects.peak_effects(energies)

    escape_peaks = []
    se_index = peak_effects_info['single_escape_peak_index']
    de_index = peak_effects_info['double_escape_peak_index']
    origin_index_se = peak_effects_info['origin_index_se']
    origin_index_de = peak_effects_info['origin_index_de']

    for i in range(len(energies)):
        if i in se_index:
            for j in range(len(se_index)):
                if i == se_index[j]:
                    escape_peaks.append('SE from ' + str(energies[origin_index_se[j]]) + ' keV peak')
        elif i in de_index:
            for k in range(len(de_index)):
                if i == de_index[k]:
                    escape_peaks.append('DE from ' + str(energies[origin_index_de[k]]) + ' keV peak')
        else:
            escape_peaks.append('None')

    #queries the nndc database from the module Becquerel for the isotopes
    #associated with every energy from the energy list.
    nndc_info = []
    for i in range(len(energies)):
         nndc_info.append(nndc.fetch_decay_radiation(t_range=[0, None], i_range=(1, None), type='Gamma', e_range=[energies[i]-1, energies[i]+1]))

    #checks to see if the 'parents' of the isotopes returned by the Becquerel
    #module are naturally occuring isotopes.
    nndc_info_verified_isotope = naa_isotope_verifier.isotope_verifier(nndc_info)['nndc_info_verified_isotope']
    nndc_info_verified_energy = naa_isotope_verifier.isotope_verifier(nndc_info)['nndc_info_verified_energy']
    nndc_info_verified_br = naa_isotope_verifier.isotope_verifier(nndc_info)['nndc_info_verified_br']

    #counts how many times an isotope is repeated in nndc_info_verified_isotope.
    #This is done for instances when multiple isotopes emit the same energy
    #photon and only one isotope can be chosen to represent a given energy.
    unpacked_isotopes = list(chain.from_iterable(nndc_info_verified_isotope))
    tally = [ (i,unpacked_isotopes.count(i)) for i in set(unpacked_isotopes) ]
    tally.sort(key=itemgetter(1), reverse=True)
    
    #chooses most probable isotope for energies in which multiple isotopes emit
    #at the same energy. Criteria is based on the total amount of times an
    #isotope appears as a possible candidate for all peak energies.

    for i in range(len(nndc_info_verified_isotope)):
        try:
            if len(nndc_info_verified_isotope[i]) > 1:
                for j in range(len(tally)):
                    if tally[j][0] in nndc_info_verified_isotope[i]:
                        index = nndc_info_verified_isotope[i].index(tally[j][0])
                        nndc_info_verified_isotope[i] = [nndc_info_verified_isotope[i][index]]
                        nndc_info_verified_energy[i] = [nndc_info_verified_energy[i][index]]
                        nndc_info_verified_br[i] = [nndc_info_verified_br[i][index]]
                        break
                    else:
                        pass
            else:
                pass
        except:
            pass

    #for every energy and branching ratio that contains an uncertainty, the
    #below code will only extract the nominal value and discard the standard
    #deviation.
    for i in range(len(nndc_info_verified_isotope)):
        try:
            if type(nndc_info_verified_energy[i][0]) == uncertainties.core.Variable:
                nndc_info_verified_energy[i][0] = nndc_info_verified_energy[i][0].nominal_value
            if type(nndc_info_verified_br[i][0]) == uncertainties.core.Variable:
                nndc_info_verified_br[i][0] = nndc_info_verified_br[i][0].nominal_value
        except:
            pass

    #since the branching ratios returned from Becquerel are not normalized to 1,
    #the below code will divide each branching ratio returned from Becquerel by 
    #100 in order to keep all the branching ratios consistent.

    for i in range(len(nndc_info_verified_isotope)):
        try:
            nndc_info_verified_br[i] = [nndc_info_verified_br[i][0] / 100]
        except:
            pass

    #Assembles the final list of isotopes that are most likely present for each
    #given energy.
    isotopes = background_isotopes[:]
    isotopes_energy = background_isotopes_energy[:]
    isotopes_br = background_isotopes_br[:]

    for i in range(len(isotopes)):
        if isotopes[i] == []:
            isotopes[i] = nndc_info_verified_isotope[i]
            isotopes_energy[i] = nndc_info_verified_energy[i]
            isotopes_br[i] = nndc_info_verified_br[i]

    for j in range(len(isotopes)):
        if j in se_index:
            index = se_index.index(j)
            try:
                isotopes[j].extend(['SE:' + isotopes[origin_index_se[index]][0]])
            except:
                isotopes[j].extend(['SE Unidentified'])
                pass
        if j in de_index:
            index = de_index.index(j)
            try:
                isotopes[j].extend(['DE:' + isotopes[origin_index_de[index]][0]])
            except:
                isotopes[j].extend(['DE Unidentified'])
                pass

    """
    results1 = {'Peak Energy (keV)':energies,'Isotope':isotopes,
                'Isotopes Branching Ratio':isotopes_br,'Net Area':net_area,
                'Net Area Uncertainty':net_area_unc,'Peak CPS':peak_cps,
                'fwhm':fwhm}

    df1 = DataFrame(results1)
    """

    #Formats the data to output to a csv file in which the isotopes will be
    #listed in descending order (along with their relevant peak information) 
    #based on the number of peak energies detected.
    unpacked_isotopes = list(chain.from_iterable(isotopes))
    tally = [ (i,unpacked_isotopes.count(i)) for i in set(unpacked_isotopes) ]
    tally.sort(key=itemgetter(1), reverse=True)

    ordered_isotopes = []
    ordered_energies = []
    ordered_br = []
#    ordered_net_area = []
#    ordered_net_area_unc = []
#    ordered_peak_cps = []
#    ordered_fwhm = []
    for i in range(len(tally)):
        ordered_isotopes.append(tally[i][0])
        temp_energies = []
        temp_br = []
 #       temp_ordered_net_area = []
 #       temp_ordered_net_area_unc = []
 #       temp_ordered_peak_cps = []        
 #       temp_ordered_fwhm = []
        for j in range(len(isotopes)):
            if tally[i][0] in isotopes[j]:
                temp_energies.append(energies[j])
 #               temp_ordered_net_area.append(net_area[j])
 #               temp_ordered_net_area_unc.append(net_area_unc[j])
 #               temp_ordered_peak_cps.append(peak_cps[j])                
 #               temp_ordered_fwhm.append(fwhm[j])

                try:
                    index = isotopes[j].index(tally[i][0])
                    temp_br.append(isotopes_br[j][index])
                except:
                    temp_br.append([None])

        ordered_energies.append(temp_energies)
        ordered_br.append(temp_br)
#        ordered_net_area.append(temp_ordered_net_area)
#        ordered_net_area_unc.append(temp_ordered_net_area_unc)
#        ordered_peak_cps.append(temp_ordered_peak_cps)        
#        ordered_fwhm.append(temp_ordered_fwhm)

#    results2 = {'isotopes':ordered_isotopes,'energies':ordered_energies,
#                'branching ratios':ordered_br,'net areas':ordered_net_area,
#                'net area uncertainties':ordered_net_area_unc,'peak cps':ordered_peak_cps,
#                'fwhm':ordered_fwhm}

    results2 = {'isotopes':ordered_isotopes,'energies':ordered_energies,'branching ratios':ordered_br}

    df2 = DataFrame(results2)

#    results2['csv_filename'] = csv_filename

#    naa_csv_maker.csv_maker(results2)

    return(df2)