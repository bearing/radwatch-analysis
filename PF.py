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
    def __init__(self, source_energies, spectrum, background = None,
                      source_activities = None, source_isotopes = None, branching_ratio = None):
        self.spectrum = spectrum
        self.background = background
        self.source_energies = source_energies

        self.source_activities = source_activities
        self.source_isotopes = source_isotopes
        self.branching_ratio = branching_ratio
        self.fitters = []

        self.integrals = []

    def calibration(self,integrals): #calculate efficiencies
        efficiencies = []
        for x in range(0,len(self.source_activities)):
            iso = bq.tools.Isotope(self.source_isotopes[x])
            efficiency = self.integrals[x]/(self.source_activities[x]*self.branching_ratio[x])
            efficiencies = np.append(efficiencies,efficiency)
        return efficiencies


    def get_counts(self):
        spec_counts = self.spectrum.counts_vals #spectrum counts

        if self.background is not None:
            bg_counts = self.background.counts_vals #background counts
            sub_spec = self.spectrum - self.background #background subtraction
            spec_counts = spec_counts - bg_counts #all counts
        else:
            bg_count = 0
            sub_spec  = self.spectrum #background is None
            spec_counts = spec_counts #all counts

        spec_energies = sub_spec.bin_centers_kev #all energues
        integrals = []
        integrals_unc = []
        model = ['gauss','line','erf']
        for i,n in enumerate(self.source_energies):
            self.fitters.append(bq.core.fitting.Fitter(model, x=sub_spec.bin_indices, y=sub_spec.cps_vals, y_unc=sub_spec.cps_uncs))
            idx = f_near(spec_energies,n)
            self.fitters[i].set_roi(idx-100,idx+100)
            self.fitters[i].fit()
            amp = self.fitters[i].result.params['gauss_amp'].value
            mu = self.fitters[i].result.params['gauss_mu'].value
            sigma =self.fitters[i].result.params['gauss_sigma'].value
            def gaussian(x):
                return (self.spectrum.livetime * amp /(m.sqrt(2*m.pi)*sigma)) * m.exp(- ((x-mu)**2) / (2*sigma**2))
            integral = integrate.quad(gaussian, idx-100, idx+100)
            integrals = np.append(integrals,integral[0])
            #calculate amp_up by amp_up = amp + amp_unc
            if self.fitters[i].result.params['gauss_amp'].stderr is not None:
                amp = self.fitters[i].result.params['gauss_amp'].value + self.fitters[i].result.params['gauss_amp'].stderr
            else:
                amp = 2.0 * self.fitters[i].result.params['gauss_amp'].value
            if self.fitters[i].result.params['gauss_sigma'].stderr is not None:
                sigma =self.fitters[i].result.params['gauss_sigma'].value + self.fitters[i].result.params['gauss_sigma'].stderr
            else:
                sigma = 2.0 * self.fitters[i].result.params['gauss_sigma'].value
            integral_up = integrate.quad(gaussian, idx-100, idx+100)
             #calculate amp_low by amp_low = amp - amp_unc
            if self.fitters[i].result.params['gauss_amp'].stderr is not None:
                amp = self.fitters[i].result.params['gauss_amp'].value - self.fitters[i].result.params['gauss_amp'].stderr
            else:
                amp = 0
            if self.fitters[i].result.params['gauss_sigma'].stderr is not None:
                sigma =self.fitters[i].result.params['gauss_sigma'].value - self.fitters[i].result.params['gauss_sigma'].stderr
            else:
                sigma = 0
            if amp == 0:
                integral_low = [0]
            else:
                integral_low = integrate.quad(gaussian, idx-100, idx+100)
            #calculate integral_unc
            integral_unc = (integral_up[0] - integral_low[0])/2
            integrals_unc = np.append(integrals_unc,integral_unc)
        self.integrals = integrals
        self.integrals_unc = integrals_unc
        return integrals, integrals_unc


    def Efficiency(self):
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
