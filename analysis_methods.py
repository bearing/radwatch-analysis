import becquerel as bq
from becquerel import Spectrum
import numpy as np
import scipy.integrate as integrate
import math as m
import importlib
import pandas as pd
import sys
import matplotlib.pyplot as plt
import csv
import PF


class Efficiency(object):
    """
    Object for undertaking the Efficiency Calibration of a detector.
    Currently only plots the Efficiency versus Energy data and the fitted curve.

    Use cases:
    
        - apply polinomial fit to input energies
    """

    def __init__(self,source_energies=[],eff=None,eff_uncer=None):
        
        self.energy = source_energies
        self.values = eff
        self.unc = eff_uncer
        self.x = []
        self.y = []
        self.space = np.linspace(1, 2160, 540)
        self.z = []
        self.fit = []
        self.new_fit = []

    def mutate(self):
        """
        Mutates data and creates the fit function.
        """
        if len(self.energy)>0:
            for i in self.energy: 
                self.x.append(np.log(i/1461))
            for i in self.values:
                self.y.append(np.log(i))
            self.z = np.polyfit(np.asarray(self.x), np.asarray(self.y), 4)
        else:
            print("Error: cannot perform fit without input energies and uncertainties!")

    def save_fit(self,filename='eff_calibration_parameters.txt'):
        with open(filename, 'w') as file:
            file_writer = csv.writer(file)
            file_writer.writerow(self.z)
            file_writer.writerow(self.values)
            file_writer.writerow(self.unc)

    def set_parameters(self,filename='eff_calibration_parameters.txt'):
        with open(filename, 'r') as file:
            file_reader = csv.reader(file)
            self.z = np.array(next(file_reader),dtype=np.float64)
            self.values = np.array(next(file_reader),dtype=np.float64)
            self.unc = np.array(next(file_reader),dtype=np.float64)
            print("Loaded fit parameters 0-4:", self.z)
            print("Loaded input energies:", self.values)
            print("Loaded energy uncertainties:", self.unc)
            if len(self.z) != 5:
                print('ERROR: file does not contain the correct number of paramters (5)')

    def normal(self, x): 
        return np.log(x/1461)

    def func3(self, x): 
        return (self.z[0]*self.normal(x)**4)+(self.z[1]*self.normal(x)**3)+(self.z[2]*self.normal(x)**2)+(self.z[3]*self.normal(x))+(self.z[4])

    def new_func(self, x): 
        return np.exp(func3(x))

    def fitting(self):
        """
        Fits the data.
        """
        for i in self.space:
            self.fit.append(self.func3(i))
        for i in self.fit:
            self.new_fit.append(np.exp(i))

    def get_eff(self,energy):
        return self.new_func(energy)

    def plotter(self,ylim=None):
        """
        Plots the data and the fit.
        """
        plt.title('Efficiency Curve')
        plt.xlabel('Energy (keV)')
        plt.ylabel('Efficiency')
        plt.errorbar(self.energy, self.values,yerr=self.unc, fmt ='ro',elinewidth=2,capsize=4)
        plt.plot(self.energy, self.values, 'ro')
        plt.grid()
        plt.plot(self.space, self.new_fit)
        plt.legend(('Data Points', 'Fitted Curve'), loc='upper right')
        if ylim is not None:
            plt.ylim(0, ylim)
        plt.savefig('eff_curve.png',dpi=200)
        plt.show()


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
