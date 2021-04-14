import argparse
parser = argparse.ArgumentParser(description="Signal processing (background subtraction) for parsed SIS3320 raw data")
parser.add_argument('filename', type=str, help="Input data file of type .spe")
args = parser.parse_args()

specname = args.filename + '.spe'

from becquerel import Spectrum
import numpy as np
import importlib
import sys
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

countrate = [i / spec.livetime for i in roi_counts]
uncrate = [i / spec.livetime for i in roi_unc]

sactivity, sactunc = [(i / j) / c.weight for i, j in zip(countrate, efficiency)], [(i / j) / c.weight for i, j in zip(uncrate, efficiency)]
for i, j, k in zip(c.source_energies, sactivity, sactunc):
    print("Specific activity at", i, "keV:", j, "±", k, "Bq/g")
    
plt.show()