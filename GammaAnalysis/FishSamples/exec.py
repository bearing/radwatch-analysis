import argparse
parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help="Input data file of type .spe")
args = parser.parse_args()

specname = args.filename + '.spe'
csvname = args.filename + 'Data.csv'

from becquerel import Spectrum
import numpy as np
import importlib
import sys
import csv
import matplotlib.pyplot as plt
sys.path.insert(0,r"C:\Users\benhu\Desktop\Research\radwatch-analysis")

import analysis_methods as am
import ROI
importlib.reload(am)
importlib.reload(ROI)

config = args.filename + 'Config'
c = __import__(config)

path = r'C:\Users\benhu\Desktop\Research\DataFiles\fishsamples2019'
spectrum = path + r'\\' + specname
background = r'C:\Users\benhu\Desktop\Research\DataFiles\fishsamples2019\background.spe'
spec = Spectrum.from_file(spectrum)
bgspec = Spectrum.from_file(background)
counts = spec.counts_vals
energies = spec.bin_centers_kev

roi = ROI.ROI(spec, bgspec, c.source_energies, c.tag)

for key in c.params:
    roi.set_sideband(int(key), c.params[key][0], c.params[key][1])
    roi.plot_peak_region(spec, c.source_energies, int(key))

roi.find_peak_energies()
roi_counts, roi_unc = roi.get_counts()

eff_func = am.Efficiency()
eff_func.set_parameters()

print(roi_counts)
print(roi_unc)

plt.show()

efficiency = [eff_func.get_eff(i) for i in c.source_energies]
efficiencyunc = [eff_func.get_eff_error(i) for i in c.source_energies]
#for i in c.source_energies:
    #efficiency.append(eff_func.get_eff(i))
    #efficiencyunc.append(eff_func.get_eff_error(i))

countrate = [i / spec.livetime for i in roi_counts]
countrateunc = [i / spec.livetime for i in roi_unc]
#actfrac = [np.exp(-1 * (np.log(2) / i) * (c.time)) for i in c.source_halflives]

volfracs = [i / c.maxvol for i in c.vol]
avgvolfrac = sum(volfracs) / len(volfracs)

def standarddeviation(lst):
    avg = sum(lst) / len(lst)
    sqrdif = [(i - avg) ** 2 for i in lst]
    return (sum(sqrdif) / len(lst)) ** 0.5

def multprop(A, a, B, b):
    #This function takes two values and two uncertainties and multiplies them together, propagates the uncertainty, and returns a tuple.
    f = A * B
    return f, abs(f) * ((((a / A) ** 2) + ((b / B) ** 2)) ** 0.5)

def divprop(A, a, B, b):
    #This function takes two values and two uncertainties and multiplies them together, propagates the uncertainty, and returns a tuple.
    f = A / B
    return f, abs(f) * ((((a / A) ** 2) + ((b / B) ** 2)) ** 0.5)

def propagate(combinedlist, proptypelist):
    #This function takes a list of lists in the format of [[Values 1],[Uncertainties 1],[Values 2],[Uncertainties 2],...] and a list of propagation types (that must be predefined to return a tuple with the format of (value, uncertainty)) at each propagation step and returns a tuple of lists with the format of ([values], [uncertainties]). If propagating any integers, make sure to expand them into a list of suitable length as well.
    if len(combinedlist) == 2:
        return combinedlist[0], combinedlist[1]
    proptype = proptypelist.pop(0)
    workinglist1 = [combinedlist.pop(0), combinedlist.pop(0)]
    workinglist2 = [combinedlist.pop(0), combinedlist.pop(0)]
    #list(map(float, combinedlist.pop(0)))
    print(workinglist1)
    print(workinglist2)
    returnlist = [[], []]
    while len(workinglist1[0]) != 0:
        A = workinglist1[0].pop(0)
        a = workinglist1[1].pop(0)
        B = workinglist2[0].pop(0)
        b = workinglist2[1].pop(0)
        value, uncertainty = proptype(A, a, B, b)
        returnlist[0].append(value)
        returnlist[1].append(uncertainty)
    combinedlist.insert(0, returnlist[1])
    combinedlist.insert(0, returnlist[0])
    return propagate(combinedlist, proptypelist)

combine = [countrate, countrateunc, efficiency, efficiencyunc, [avgvolfrac] * 5, [standarddeviation(c.vol) / c.maxvol] * 5]
proptype = [divprop, divprop]
sactivity, sactunc = propagate(combine, proptype)

#sd = standarddeviation(c.vol) / c.maxvol #sd for volfrac
    
#sactivity = [(((i / j) / (c.weight / 1000)) / avgvolfrac) for i, j in zip(countrate, efficiency)]  #reinstate activity fraction due to half-lives later

#sactunc = [multprop(i, j, avgvolfrac, sd) for i, j in zip(sactivity, [((i / j) / (c.weight / 1000)) for i, j in zip(uncrate, efficiency)])]

#sactivity, sactunc = [(((i / j) / (c.weight / 1000)) / avgvolfrac) / z for i, j, z in zip(countrate, efficiency, actfrac)], [(((i / j) / (c.weight / 1000)) / avgvolfrac) / z for i, j, z in zip(uncrate, efficiency, actfrac)]

with open(csvname, mode='w') as csvfile:
    csvfiler = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for i, j, k in zip(c.source_energies, sactivity, sactunc):
        print("Specific activity at", i, "keV:", j, "±", k, "Bq/kg")
        csvfiler.writerow([i, j, k])
    #csvfiler.writerow([sd])
    
