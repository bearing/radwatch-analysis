import numpy as np

def peak_effects(energies):
    """
    This module checks to see if a given list of peak energies contains any
    possible single escape peaks, double escape peaks, and sum peaks.
    """

    single_escape_peak = []
    single_escape_peak_index = []
    double_escape_peak = []
    double_escape_peak_index = []

    for i in range(len(energies)):
        #checks to see if condition for escape peaks is fulfilled.
        if energies[i] >= float(1022):
            for j in range(len(energies)):
                #checks to see if peak is a single escape peak.
                if np.isclose(energies[i],energies[j]+511,atol=1) == True:
                    single_escape_peak.append(energies[j])
                    single_escape_peak_index.append(j)
                #checks to see if peak is a double escape peak.
                if np.isclose(energies[i],energies[j]+1022,atol=1) == True:
                    double_escape_peak.append(energies[j])
                    double_escape_peak_index.append(j)
                    """
                    for m in range(len(energies)):
                        if np.isclose(energies[j],energies[m]+511,atol=1) == True:
                            double_escape_peak.append(energies[m])
                            double_escape_peak_index.append(m)
                    """
    #gets rid of the single escape peak that has the same value as a double
    #escape peak(s).
    double_count = []
    double_count_index = []

    for i in range(len(single_escape_peak)):
        for j in range(len(double_escape_peak)):
            if single_escape_peak[i] == double_escape_peak[j]:
                double_count.append(single_escape_peak[i])
                double_count_index.append(energies.index(single_escape_peak[i]))

    single_escape_peak = [x for x in single_escape_peak if x not in double_count]
    single_escape_peak_index = [x for x in single_escape_peak_index if x not in double_count_index]

    #finds the index of the original energy that is responsible for the single
    #escape peaks and the double escape peaks.
    origin_index_se = []
    origin_index_de = []
    for i in range(len(energies)):
        for j in range(len(single_escape_peak)):
            if np.isclose(energies[i],single_escape_peak[j]+511,atol=1) == True:
                origin_index_se.append(i)
        for k in range(len(double_escape_peak)):
            if np.isclose(energies[i],double_escape_peak[k]+1022,atol=1) == True:
                origin_index_de.append(i)

    peak_effects = {'single_escape_peak':single_escape_peak,'double_escape_peak':double_escape_peak,
                    'single_escape_peak_index':single_escape_peak_index,'double_escape_peak_index':double_escape_peak_index,
                    'origin_index_se':origin_index_se,'origin_index_de':origin_index_de}

    return(peak_effects)