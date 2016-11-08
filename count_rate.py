import Gamma_Analysis as ga

def count_rate(M, B, energy):
    """
    Takes in a measured and background spectra and a peak energy and return the 
    net area under the peak.
    """
    pm_results = ga.peak_measurement(M, energy, sub_regions='none')
    bm_results = ga.peak_measurement(B, energy, sub_regions='none')
    sub_peak = ga.background_subtract(pm_results, bm_results, M.livetime,
                                   B.livetime)
    net_area = sub_peak[0]
    count_rate = net_area/M.livetime
    
    return(count_rate)