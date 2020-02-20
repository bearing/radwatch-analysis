#Austin's PF script
import becquerel as bq
from becquerel import Spectrum
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import math as m

#INPUT: source_energies, spectrum, background, branching_ratio


def f_near(energy_array,energy): #finds index of closest energy in spectrum to that of the characteristic energy
    idx = np.abs(energy_array - energy).argmin()
    return idx

class PF(object):
    def __init__(self,source_energies,source_activities,spectrum,background,branching_ratio):
        self.source_energies = source_energies
        self.source_activities = source_activities
        self.spectrum = spectrum
        self.background = background
        self.branching_ratio = branching_ratio



    def get_counts(self):
        spec = Spectrum.from_file(self.spectrum) #import spectrum data
        spec_counts = spec.counts_vals #spectrum counts
        bg = Spectrum.from_file(self.background) #import spectrum data
        bg_counts = bg.counts_vals #background counts
        sub_spec = spec - bg #background subtraction
        spec_energies = sub_spec.energies_kev #all energues
        spec_counts = spec_counts - bg_counts #all counts
        integrals = []
        model = ['gauss','line','erf']
        for n in self.source_energies:
            fit = bq.core.fitting.Fitter(model, x=sub_spec.bin_indices, y=sub_spec.cps_vals, y_unc=sub_spec.cps_uncs)
            idx = f_near(spec_energies,n)
            fit.set_roi(idx-100,idx+100)
            fit.fit()
            amp = fit.result.params['gauss_amp'].value
            mu = fit.result.params['gauss_mu'].value
            sigma =fit.result.params['gauss_sigma'].value
            def gaussian(x):
                return (spec.livetime * amp /(m.sqrt(2*m.pi)*sigma)) * m.exp(- ((x-mu)**2) / (2*sigma**2))
            integral = integrate.quad(gaussian, idx-100, idx+100)
            integrals = np.append(integrals,integral[0])
        return integrals

    def Efficiency(self):
        def calibration(integrals): #calculate efficiencies
            efficiencies = []
            for x in range(0,len(self.source_activities)):
                iso = bq.tools.Isotope(self.source_isotopes[x])
                efficiency = integrals[x]/(self.source_activities[x]*branching_ratio[x])
                efficiencies = np.append(efficiencies,efficiency)
            return efficiencies
        spec = Spectrum.from_file(self.spectrum) #import spectrum data
        spec_counts = spec.counts_vals #spectrum counts
        bg = Spectrum.from_file(self.background) #import spectrum data
        bg_counts = bg.counts_vals #background counts
        sub_spec = spec - bg #background subtraction
        spec_energies = sub_spec.energies_kev #all energues
        spec_counts = spec_counts - bg_counts #all counts
        integrals = []
        model = ['gauss','line','erf']
        for n in self.source_energies:
            fit = bq.core.fitting.Fitter(model, x=sub_spec.bin_indices, y=sub_spec.cps_vals, y_unc=sub_spec.cps_uncs)
            idx = f_near(spec_energies,n)
            fit.set_roi(idx-100,idx+100)
            fit.fit()
            amp = fit.result.params['gauss_amp'].value
            mu = fit.result.params['gauss_mu'].value
            sigma =fit.result.params['gauss_sigma'].value
            def gaussian(x):
                return (spec.livetime * amp /(m.sqrt(2*m.pi)*sigma)) * m.exp(- ((x-mu)**2) / (2*sigma**2))
            integral = integrate.quad(gaussian, idx-100, idx+100)
            integrals = np.append(integrals,integral[0])
        efficiencies = calibration(integrals)
        return efficiencies
