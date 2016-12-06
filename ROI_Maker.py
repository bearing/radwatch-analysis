import SPEFile
from Updated_Peak_Finder import peak_finder_pro as peak_finder
import Gamma_Isotopes
import Gamma_Analysis

def ROI_Maker(spectra, use='NAA'):

    """
    Takes in a measured spectra and identifies peaks in terms of channel number
    and energy. Also returns peak and compton ROIs as well as each ROIs gross 
    area.
    """

    peak_channels = peak_finder(spectra)
    zero_offset = spectra.energy_cal[0]
    energy_per_channel = spectra.energy_cal[1]
    
    peak_energies = []

    center_peak_region = []
    left_peak_region = []
    right_peak_region = []
    
    region_size = 1.3
    compton_distance = 4
      
    if use == 'NAA':  
        for i in range(len(peak_channels)):
            peak_energies.append(energy_per_channel*peak_channels[i]+zero_offset)

    
    if use == 'GA':
        energies_of_interest = [Gamma_Isotopes.actinium_228.list_sig_g_e, 
                                Gamma_Isotopes.bismuth_214.list_sig_g_e, 
                                Gamma_Isotopes.caesium_134.list_sig_g_e, 
                                Gamma_Isotopes.caesium_137.list_sig_g_e, 
                                Gamma_Isotopes.cobalt_60.list_sig_g_e, 
                                Gamma_Isotopes.lead_210.list_sig_g_e, 
                                Gamma_Isotopes.lead_212.list_sig_g_e, 
                                Gamma_Isotopes.lead_214.list_sig_g_e, 
                                Gamma_Isotopes.potassium_40.list_sig_g_e, 
                                Gamma_Isotopes.thallium_208.list_sig_g_e, 
                                Gamma_Isotopes.thorium_234.list_sig_g_e]
                                
        peak_energies_original = [val for sublist in energies_of_interest for val in sublist]
        peak_energies_original.sort()
        peak_energies = []
        
        for i in range(len(peak_energies_original)):
            peak_energies.append(Gamma_Analysis.peak_finder(spectra, peak_energies_original[i]))
       
        peak_channels = []
        
        for i in range(len(peak_energies)):
            peak_channels.append((peak_energies[i]-zero_offset)/energy_per_channel)
            
        
    for i in range(len(peak_energies)):
        fwhm = 0.05*peak_energies[i]**0.5
        fwhm_channel = int(region_size*(fwhm-zero_offset)/energy_per_channel)
        
        """
        Center Peak
        """
        center_peak_region.append(peak_channels[i] - fwhm_channel)
        center_peak_region.append(peak_channels[i] + fwhm_channel) 
        """
        Left Peak
        """
        left_peak = peak_channels[i] - compton_distance * fwhm_channel
        left_peak_region.append(left_peak - fwhm_channel)
        left_peak_region.append(left_peak + fwhm_channel)
        """
        Right Peak
        """
        right_peak = peak_channels[i] + compton_distance * fwhm_channel
        right_peak_region.append(right_peak - fwhm_channel)
        right_peak_region.append(right_peak + fwhm_channel)

    ROI_info = [peak_channels, peak_energies, center_peak_region, 
                left_peak_region, right_peak_region]
            
 
    return(ROI_info)
                          
                          
def test1():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement)
    return info
    
def test2():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement)
    return info
    
def test3():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement)
    return info

def test4():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement)
    return info    
    
def test5():
    measurement = SPEFile.SPEFile('UCB007_Brazil_Nuts.Spe')
    measurement.read()
    info = ROI_Maker(measurement, use='GA')
    return info