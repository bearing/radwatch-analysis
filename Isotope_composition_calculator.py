import numpy as np
from becquerel.tools.isotope import Isotope
from becquerel.tools.isotope_qty import IsotopeQuantity, NeutronIrradiation
import datetime
from becquerel import Spectrum
import efficiencies as ef
from bs4 import BeautifulSoup
import urllib.request
import math
import NAA_Isotopes as na
from uncertainties import ufloat



#load a spectra for testing
spec_S1 = Spectrum.from_file('/Users/jackiegasca/Documents/spectras/Sample1_30m_C.Spe')

back_spec = Spectrum.from_file('/Users/jackiegasca/Documents/2017.5.1_long_background.Spe')


#For now, just use an existing dictionary/class of isotopes
spec_S1_ener_spec = spec_S1.energies_kev[0:len(spec_S1)]
back_ener_spec = back_spec.energies_kev[0:len(back_spec)]

isotope_list = [na.Br_82, na.Na_24, na.Sb_122, na.K_42]
#Info regarding the irradiation:
irr_start = '2017-04-27 14:02:00'
irr_stop = '2017-04-27 14:12:00'
flux = 3.1e11
N_0 = 6.02e23

def IsotopeActivity():
    iso_name = []
    iso_energy = []
    iso_cps = []
    iso_br = []
    for iso in isotope_list:

        E = iso.energies['energy'][0]
        FWHM = ((2.355 * (0.09 * 0.00296 * E) ** 0.5) ** 2
                + (1.3) ** 2) ** 0.5 #keV
        start = E - 1 * FWHM
        end = E + 1 * FWHM
        bkgd_start = E - 2 * FWHM
        bkgd_end = E + 2 * FWHM

        en = (np.abs(spec_S1_ener_spec - E)).argmin()
        val1 = (np.abs(spec_S1_ener_spec - start)).argmin()
        val2 = (np.abs(spec_S1_ener_spec - end)).argmin()
        val3 = (np.abs(spec_S1_ener_spec - bkgd_start)).argmin()
        val4 = (np.abs(spec_S1_ener_spec - bkgd_end)).argmin()

        cps_values = spec_S1.cps_vals[val1:val2]
        max_cps_index = np.argmax(cps_values)
        ex_val = max_cps_index - (en - val1)
        val1 = val1 + ex_val
        val2 = val2 + ex_val
        val3 = val3 + ex_val
        val4 = val4 + ex_val

        peak_vals = spec_S1.cps_vals[val1:val2]
        back_vals = back_spec.cps_vals[val1:val2]
        peak_vals_sub = [a - b for a, b in zip(peak_vals, back_vals)]

        bkgd_vals1 = spec_S1.cps_vals[val3:val1 - 1]
        back_bkgd_vals1 = back_spec.cps_vals[val3:val1 - 1]

        bkgd_vals2 = spec_S1.cps_vals[val2 + 1:val4]
        back_bkgd_vals2 = back_spec.cps_vals[val2+1:val4]

        back_sub1 = [a - b for a, b in zip(bkgd_vals1, back_bkgd_vals1)]
        back_sub2 = [a - b for a, b in zip(bkgd_vals2, back_bkgd_vals2)]

        bkgd_cps = (sum(back_sub1) + sum(back_sub2)) / (len(back_sub1)
                    + len(back_sub2))
        peak_vals[:] = [x - bkgd_cps for x in peak_vals_sub]
        peak_cps = sum(peak_vals)

        name = '{0}_{1}'.format(iso.Symbol, iso.A + 1)
        iso_name.append(name)
        iso_energy.append(E)
        iso_cps.append(peak_cps)
        iso_br.append(iso.energies['branching_ratio'][0])
    #return(iso_name, iso_energy, iso_cps, iso_br)
    isotope_activities = []
    stat_uncertainties = []
    for j in range(len(iso_name)):
        ef_en = (np.abs(ef.x - iso_energy[j])).argmin()
        stat_unc = (((iso_cps[j]) ** 0.5) / (spec_S1.livetime ** 0.5)) / (ef.high[ef_en] * iso_br[j])
        activ = iso_cps[j] / (ef.high[ef_en] * iso_br[j])
        isotope_activities.append(activ)
        stat_uncertainties.append(stat_unc)
    return(iso_name, iso_energy, iso_cps, iso_br, isotope_activities, stat_uncertainties)
    for n in range(len(isotope_activities)):
        #statement = 'The activity of ' + '{0}'.format(iso_name[n]) + ' at ' + '{0}'.format(spec_S1.start_time) + ' is ' + '{0}'.format(iso_cps[n])
        statement = 'The activity of {0} at {1} is {2} bq'.format(iso_name[n], spec_S1.start_time, iso_cps[n])
        print(statement)


lists = IsotopeActivity()
iso_cps = lists[2]
iso_name = lists[0]
iso_energy = lists[1]
iso_br = lists[3]
isotope_activities = lists[4]
stat_uncertainties = lists[5]

#Remove any negative activity from the queue
def Remover():
    for i in iso_cps:
        if i <= 0:
            n = iso_cps.index(i)
            iso_name.remove(iso_name[n])
            iso_energy.remove(iso_energy[n])
            iso_br.remove(iso_br[n])
            isotope_activities.remove(isotope_activities[n])
            iso_cps.remove(iso_cps[n])
            stat_uncertainties.remove(stat_uncertainties[n])
        else:
            pass
    return(iso_name, iso_cps, iso_energy, iso_br, isotope_activities, stat_uncertainties)

lists = Remover()
lists = Remover()
lists = Remover()

def Concentration():
    conc = []
    for i in range(len(iso_name)):
        c = iso_name[i].split('_')
        abb = c[0]
        A = int(c[1])
        A_0 = A - 1
        iso_2 = '{0}-{1}'.format(abb, A_0)
        iso_1 = '{0}-{1}'.format(abb, A)
        nuclide = Isotope(iso_1)
        def urlcreator(abb, A_0):
            A_num = str(A_0)
            if len(A_num) == 1:
                A_num = '00' + A_num
            elif len(A_num) == 2:
                A_num = '0' + A_num
            else:
                A_num = A_num
            url = 'http://wwwndc.jaea.go.jp/cgi-bin/Tab80WWW.cgi?/data' \
                    + '/JENDL/JENDL-4-prc/intern/' + abb + A_num + '.intern'
            html = urllib.request.urlopen(url)
            bslink = BeautifulSoup(html, 'lxml')

            return(bslink)

        bslink = urlcreator(abb, A_0)
        def tabledata(bslink):
            '''extracts data from the jaea website'''

            table = bslink.table
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]

                if len(row) == 7:
                    if row[0] == 'total       ':
                        x_sec = row[1]
                        x_sec_s = x_sec.split(' ')
                        x_val = float(x_sec_s[0])
                        barn = x_sec_s[1]
                        if barn[1] == 'k':
                            x_val = 10**(3) * x_val
                            return(x_val)
                        elif barn[1] == 'm':
                            x_val = 10**(-3) * x_val
                            return(x_val)

                        elif barn[1] == '&':
                            x_val = 10**(-6) * x_val
                            return(x_val)
                        else:
                            x_val = x_val
                            return(x_val)

                    else:
                        pass

                else:
                    pass
            return(x_val)

        x_val = tabledata(bslink)
        #print(x_val)

        quantity = IsotopeQuantity(nuclide, date=spec_S1.start_time, bq=isotope_activities[i])
        unc_quantity = IsotopeQuantity(nuclide, date=spec_S1.start_time, bq=stat_uncertainties[i])
        irrad_quan = quantity.bq_at(irr_stop)
        unc_irrad_quan = unc_quantity.bq_at(irr_stop)
        irrad_act = IsotopeQuantity(nuclide, date=irr_stop, bq=irrad_quan)
        unc_irrad_act = IsotopeQuantity(nuclide, date=irr_stop, bq=unc_irrad_quan)
        ni = NeutronIrradiation(irr_start, irr_stop, n_cm2_s=flux)
        init_comp = ni.activate(x_val, initial=Isotope(iso_2), activated=irrad_act)
        unc_init_comp = ni.activate(x_val, initial=Isotope(iso_2), activated=unc_irrad_act)
        init_comp.is_stable = True
        unc_init_comp.is_stable = True
        sinit_comp = str(init_comp)
        sunc_init_comp = str(unc_init_comp)
        #print(sinit_comp, sunc_init_comp)
        s2 = sinit_comp.split(' ')
        s0 = s2[0]
        sunc2 = sunc_init_comp.split(' ')
        sunc0 = sunc2[0]
        isotope_type = ' ' + s2[1] + ' ' + s2[2] + ' ' + s2[3]
        print(s0+' +/- '+sunc0 +isotope_type)

        #conc.extend[str(init_comp)]
    #return(conc)

Concentration()
