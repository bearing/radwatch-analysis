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

efficiency = []
for i in c.source_energies:
    efficiency.append(eff_func.get_eff(i))

print(roi_counts)
print(roi_unc)
    
plt.show()
    
countrate = [i / spec.livetime for i in roi_counts]
uncrate = [i / spec.livetime for i in roi_unc]
#actfrac = [np.exp(-1 * (np.log(2) / i) * (c.time)) for i in c.source_halflives]

volfracs = [i / c.maxvol for i in c.vol]
avgvolfrac = sum(volfracs) / len(volfracs)

def standarddeviation(lst):
    avg = sum(lst) / len(lst)
    sqrdif = [(i - avg) ** 2 for i in lst]
    return (sum(sqrdif) / len(lst)) ** 0.5

def multprop(A, a, B, b):
    f = A * B
    return f * ((((a / A) ** 2) + ((b / B) ** 2)) ** 0.5)

sd = standarddeviation(c.vol) / c.maxvol #sd for volfrac
    
sactivity = [(((i / j) / (c.weight / 1000)) / avgvolfrac) for i, j in zip(countrate, efficiency)]  #reinstate activity fraction due to half-lives later

sactunc = [multprop(i, j, avgvolfrac, sd) for i, j in zip(sactivity, [((i / j) / (c.weight / 1000)) for i, j in zip(uncrate, efficiency)])]
                                                                                                               
#sactivity, sactunc = [(((i / j) / (c.weight / 1000)) / avgvolfrac) / z for i, j, z in zip(countrate, efficiency, actfrac)], [(((i / j) / (c.weight / 1000)) / avgvolfrac) / z for i, j, z in zip(uncrate, efficiency, actfrac)]

with open(csvname, mode='w') as csvfile:
    csvfiler = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for i, j, k in zip(c.source_energies, sactivity, sactunc):
        print("Specific activity at", i, "keV:", j, "±", k, "Bq/kg")
        csvfiler.writerow([i, j, k])
    #csvfiler.writerow([sd])
    
