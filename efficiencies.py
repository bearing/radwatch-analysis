import numpy as np
import matplotlib.pyplot as plt
from becquerel.tools.isotope import Isotope
from becquerel.tools.isotope_qty import IsotopeQuantity, NeutronIrradiation
import datetime
from becquerel import Spectrum
import Calibration_sources as ca
from scipy.optimize import curve_fit

"""creates efficiency data needed to calculate concetrations of
isotopes present in the measured samples"""

#create a queue of the calibration sources used
Na_22_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Na_22_flat_against_detector_531.Spe')
Mn_54_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Mn_54_flat_against_detector_1264-96-2.Spe')
Co_57_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Co_57_flat_against_detector_1264-96-3.Spe')
Cd_109_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Cd_109_flat_against_detector_1264-96-8.Spe')
Th_228_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Th_228_flat_against_detector_1415-83.Spe')
Eu_152_spec = Spectrum.from_file('/Users/jackiegasca/Documents/Ca_sources/Eu_152_flat_against_detector_1316-97-2.Spe')


Na_22_start = Na_22_spec.start_time
Mn_54_start = Mn_54_spec.start_time
Co_57_start = Co_57_spec.start_time
Cd_109_start = Cd_109_spec.start_time
Th_228_start = Th_228_spec.start_time
Eu_152_start = Eu_152_spec.start_time

Na_22_init_act = IsotopeQuantity('na22', date=ca.Na_22.date, uci=ca.Na_22.init_act)
Na_22_act = Na_22_init_act.bq_at(Na_22_start)
Mn_54_init_act = IsotopeQuantity('mn54', date=ca.Mn_54.date, uci=ca.Mn_54.init_act)
Mn_54_act = Mn_54_init_act.bq_at(Mn_54_start)
Co_57_init_act = IsotopeQuantity('co57', date=ca.Co_57.date, uci=ca.Co_57.init_act)
Co_57_act = Co_57_init_act.bq_at(Co_57_start)
Cd_109_init_act = IsotopeQuantity('cd109', date=ca.Cd_109.date, uci=ca.Cd_109.init_act)
Cd_109_act = Cd_109_init_act.bq_at(Cd_109_start)
Th_228_init_act = IsotopeQuantity('th229', date=ca.Th_228.date, uci=ca.Th_228.init_act)
Th_228_act = Th_228_init_act.bq_at(Th_228_start)
Eu_152_init_act = IsotopeQuantity('eu152', date=ca.Eu_152.date, uci=ca.Eu_152.init_act)
Eu_152_act = Eu_152_init_act.bq_at(Eu_152_start)

Na_22_ener_spec = Na_22_spec.energies_kev[0:len(Na_22_spec)]
Mn_54_ener_spec = Mn_54_spec.energies_kev[0:len(Mn_54_spec)]
Co_57_ener_spec = Co_57_spec.energies_kev[0:len(Co_57_spec)]
Cd_109_ener_spec = Cd_109_spec.energies_kev[0:len(Cd_109_spec)]
Th_228_ener_spec = Th_228_spec.energies_kev[0:len(Th_228_spec)]
Eu_152_ener_spec = Eu_152_spec.energies_kev[0:len(Eu_152_spec)]

class UsedSources(object):
    def __init__(self, source, spec, act, ener_spec):
        self.source = source
        self.spec = spec
        self.act = act
        self.ener_spec = ener_spec

Na_22 = UsedSources(ca.Na_22, Na_22_spec, Na_22_act, Na_22_ener_spec)
Mn_54 = UsedSources(ca.Mn_54, Mn_54_spec, Mn_54_act, Mn_54_ener_spec)
Co_57 = UsedSources(ca.Co_57, Co_57_spec, Co_57_act, Co_57_ener_spec)
Cd_109 = UsedSources(ca.Cd_109, Cd_109_spec, Cd_109_act, Cd_109_ener_spec)
Th_228 = UsedSources(ca.Th_228, Th_228_spec, Th_228_act, Th_228_ener_spec)
Eu_152 = UsedSources(ca.Eu_152, Eu_152_spec, Eu_152_act, Eu_152_ener_spec)


library = ca.Calibration.ca_isotopes
print(library)

ca_list = [Na_22, Mn_54, Co_57, Cd_109, Eu_152]

#start with Na22
def efficiency_calc():
    en_eff = []

    for iso in ca_list:
        def indiveff():
            iso_eff = []

            for i in range(len(iso.source.Peak)):

                E_gamma = iso.source.Peak[i]
                FWHM = ((2.355 * (0.09 * 0.00296 * E_gamma) ** 0.5) ** 2
                        + (1.3) ** 2) ** 0.5 #keV
                sigma = FWHM / 2.355
                start = E_gamma - 2 * FWHM
                end = E_gamma + 2 * FWHM
                bkgd_start = E_gamma - 4 * FWHM
                bkgd_end = E_gamma + 4 * FWHM

                val1 = (np.abs(iso.ener_spec - start)).argmin()
                val2 = (np.abs(iso.ener_spec - end)).argmin()
                val3 = (np.abs(iso.ener_spec - bkgd_start)).argmin()
                val4 = (np.abs(iso.ener_spec - bkgd_end)).argmin()

                peak_vals = iso.spec.cps_vals[val1:val2]
                bkgd_vals1 = iso.spec.cps_vals[val3:val1 - 1]
                bkgd_vals2 = iso.spec.cps_vals[val2 + 1:val4]

                bkgd_cps = (sum(bkgd_vals1) + sum(bkgd_vals2)) / (len(bkgd_vals1)
                            + len(bkgd_vals2))
                peak_vals[:] = [x - bkgd_cps for x in peak_vals]
                peak_cps = sum(peak_vals)

                eff = peak_cps / (iso.source.Intensity[i] * iso.act)
                pair = [E_gamma, eff]
                iso_eff.append(pair)

            return iso_eff

        en_eff.extend(indiveff())

    ener_list = sorted(en_eff, key=lambda energy: energy[0])
    energy = [item[0] for item in ener_list]
    effic = [item[1] for item in ener_list]
    return(energy, effic)

[en, eff] = efficiency_calc()
print(en,eff)

def fitter(x, a, b, c, d):
    return(np.exp(a + b*np.log(x/1460) + c*(np.log(x/1460))**2 + d*(np.log(x/1460))**3))

popt,pcov = curve_fit(fitter, en, eff)

fit = []
x = np.arange(50, 2500, 1)
for i in range(len(x)):
    fit.append(fitter(x[i],popt[0],popt[1],popt[2],popt[3]))

x_index = []
for i in en:
    value = (np.abs(i - x)).argmin()
    x_index.append(value)
    #return(x_values)

differences = []
for i in range(len(x_index)):
    ind = x_index[i]
    diff = np.abs(eff[i] - fit[ind])
    differences.append(diff)

subs = np.mean(differences)
low = [a - subs for a in fit]
high = [a + subs for a in fit]
#for i in x_index:
#    print(fit[i])

plt.fill_between(x, low, high, color='pink')
plt.plot(en, eff, '*')
plt.plot(x, fit, color='black')
plt.show()

"""
plt.plot(x, fit)
plt.plot(en, eff, '*')
plt.show()
"""
