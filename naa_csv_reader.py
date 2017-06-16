import csv

def csv_reader(csv_filename):

    """
    This module reads the csv file for a specified spectrum that contains the
    peak information in a single column. This module will extract the peak
    energies as well as their associated net area with uncertainty and FWHM.
    """

    file = open(csv_filename,'r')
    read_file = csv.reader(file)
    raw_data = list(read_file)

    energies = []
    net_area = []
    net_area_unc = []
    peak_cps = []    
    fwhm = []

    for i in range(len(raw_data[2:])):
        energies.append(raw_data[2+i][0])
        net_area.append(raw_data[2+i][1])
        net_area_unc.append(raw_data[2+i][2])
        peak_cps.append(raw_data[2+i][3])        
        fwhm.append(raw_data[2+i][4])

    energies = [float(x) for x in energies]
    net_area = [float(x) for x in net_area]
    net_area_unc = [float(x) for x in net_area_unc]
    peak_cps = [float(x) for x in peak_cps]
    fwhm = [float(x) for x in fwhm]

    peak_info = {'energies':energies,'net_area':net_area,'net_area_unc':net_area_unc,'peak_cps':peak_cps,'fwhm':fwhm,'csv_filename':csv_filename}

    return(peak_info)