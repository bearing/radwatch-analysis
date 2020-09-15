import becquerel as bq
from becquerel import Spectrum
import numpy as np
import scipy.integrate as integrate
import math as m
import importlib
import pandas as pd
import sys
import matplotlib.pyplot as plt
import PF

    #input spectra and energy calibration
def apply_ecal(spec, e_cal):
    e_cal_energies=e_cal[:,0]
    e_cal_channels=e_cal[:,1]
    cal = bq.LinearEnergyCal.from_points(e_cal_channels,e_cal_energies)
    spec.apply_calibration(cal)
    return spec

def get_energies(spec):
    kernel = bq.GaussianPeakFilter(4250,30, fwhm_at_0=10)
    finder = bq.PeakFinder(spec, kernel)
    plt.figure()
    plt.plot(spec.counts_vals.clip(1e-1), label='Raw spectrum')
    plt.plot(finder._peak_plus_bkg.clip(1e-1), label='Peaks+Continuum')
    plt.plot(finder._bkg.clip(1e-1), label='Continuum')
    plt.plot(finder._signal.clip(1e-1), label='Peaks')
    plt.yscale('log')
    plt.xlim(0, len(spec))
    plt.ylim(3e-1)
    plt.xlabel('Channels')
    plt.ylabel('Counts')
    plt.legend()
    plt.tight_layout()

    finder.reset()
    finder.find_peaks(min_snr=10, xmin=50)

    plt.figure()
    plt.title('find_peaks')
    finder.plot()
    plt.tight_layout()

    energies = np.take(spec.bin_edges_kev,finder.centroids)
    energies = energies[0:-2]
    energies = energies.astype(int)
    return energies

def get_counts(cal_spec,cal_bg_spec,energies): #input energies
    peakfitter = PF.PF(spectrum = cal_spec, background = cal_bg_spec,source_energies = np.array(energies))
    peak_counts, uncertainties = peakfitter.get_counts()

    return peak_counts, uncertainties

def peakfit(peak_counts, uncertainties):
    for i in range(len(peak_counts)):
        try:
            peakfitter.fitters[i].custom_plot()
        except:
            pass
    #determine where to cut off overflow bin
    #organize into matrix [energy;count(30min);count(3hr);count(24hr)]
    return

def matrix(counts_list,energies_list):
    m1 = {'energies':energies_list[1],'counts':counts_list[1]}
    m2 = {'energies':energies_list[2],'counts':counts_list[2]}
    m3 = {'energies':energies_list[3],'counts':counts_list[3]}

    df1 = pd.DataFrame(m1)
    df2 = pd.DataFrame(m2)
    df3 = pd.DataFrame(m3)

    ordered_set = pd.merge_ordered(df1,df2,df3)
    return ordered_set

def iso_activity(peak_counts,br,ϵ):
    A = (peak_counts/(ϵ*br))
    return A

def get_dt(spectrum,t0):
    dt = spectrum.start_time.timestamp() - t0
    return  dt

def element_weight(Activity, M_A,iso_abundance,hl,flux,xs,Tirrad,dt):
    ew = ((Activity) * (M_A/(6.022*10**23))*(hl/m.log(2))*(m.exp((dt*m.log(2))/hl)/(flux*xs*Tirrad)))/iso_abundance
    return ew
