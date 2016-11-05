import SPEFile
from Updated_Peak_Finder import peak_finder_pro as peak_finder

def ROI_Maker(spectra, subregion='both'):

    """
    Takes in a measured spectra and identifies peaks in terms of channel number
    and energy. Also returns peak and compton ROIs as well as each ROIs gross 
    area.
    """

    peak_channels = peak_finder(spectra)

    counts = spectra.data    
    zero_offset = spectra.energy_cal[0]
    energy_per_channel = spectra.energy_cal[1]
    
    peak_energies = []

    center_peak_region = []
    left_peak_region = []
    right_peak_region = []
    
    center_peak_region_counts = []
    left_peak_region_counts = []
    right_peak_region_counts = []
    
    region_size = 1.3
    compton_distance = 4
        
    for i in range(len(peak_channels)):
        peak_energies.append(energy_per_channel*peak_channels[i]+zero_offset)
        
        
    for i in range(len(peak_channels)):
        fwhm = 0.05*peak_energies[i]**0.5
        fwhm_channel = int(region_size*(fwhm-zero_offset)/energy_per_channel)
        
        """
        Center Peak
        """
        center_peak_region.append(peak_channels[i] - fwhm_channel)
        center_peak_region.append(peak_channels[i] + fwhm_channel) 
        center_peak_region_counts.append(
        sum(counts[center_peak_region[-2]:center_peak_region[-1]]))
        """
        Left Peak
        """
        left_peak = peak_channels[i] - compton_distance * fwhm_channel
        left_peak_region.append(left_peak - fwhm_channel)
        left_peak_region.append(left_peak + fwhm_channel)
        left_peak_region_counts.append(
        sum(counts[left_peak_region[-2]:left_peak_region[-1]]))
        """
        Right Peak
        """
        right_peak = peak_channels[i] + compton_distance * fwhm_channel
        right_peak_region.append(right_peak - fwhm_channel)
        right_peak_region.append(right_peak + fwhm_channel)
        right_peak_region_counts.append(
        sum(counts[right_peak_region[-2]:right_peak_region[-1]]))

    ROI_info = [peak_channels, peak_energies, center_peak_region, 
                left_peak_region, right_peak_region, center_peak_region_counts, 
                left_peak_region_counts, right_peak_region_counts]

    if subregion == 'left':
        ROI_info = [ROI_info[0], ROI_info[1], ROI_info[2], ROI_info[3], 
                    ROI_info[5], ROI_info[6]]
    elif subregion == 'right':
        ROI_info = [ROI_info[0], ROI_info[1], ROI_info[2], ROI_info[4], 
                    ROI_info[5], ROI_info[7]]
    elif subregion == 'none':
        ROI_info = [0, 0, 0, 0, 0, 0] 
    
    return(ROI_info)
                          
                          
def test1():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement)
    return info
    
def test2():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement,subregion='left')
    return info
    
def test3():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement,subregion='right')
    return info

def test4():
    measurement = SPEFile.SPEFile('UCB018_Soil_Sample010_2.Spe')
    measurement.read()
    info = ROI_Maker(measurement,subregion='none')
    return info    