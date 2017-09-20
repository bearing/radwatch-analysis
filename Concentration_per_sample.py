import numpy as np
from becquerel.tools.isotope import Isotope
from becquerel.tools.isotope_qty import IsotopeQuantity, NeutronIrradiation
import datetime
from becquerel import Spectrum
import efficiencies as ef
import pottery_efficiency as pe
from bs4 import BeautifulSoup
import urllib.request
import math
import NAA_Isotopes as na
import spreadsheets as sp

#load a spectra for testing
spec_S1 = Spectrum.from_file('/Users/jackiegasca/Documents/spectras/Sample4_24h_C.Spe')

back_spec = Spectrum.from_file('/Users/jackiegasca/Documents/2017.5.1_long_background.Spe')
back_spec_ener_spec = back_spec.energies_kev[0:len(back_spec)]

#For now, just use an existing dictionary/class of isotopes
spec_S1_ener_spec = spec_S1.energies_kev[0:len(spec_S1)]

irr_start = '2017-04-27 14:02:00'
irr_stop = '2017-04-27 14:12:00'
flux = 3.1e11
N_0 = 6.02e23

def IsotopeActivity():
    iso_name = sp.Sample4_24h.element
    iso_energy = sp.Sample4_24h.energy
    en_counts = sp.Sample4_24h.counts
    print(en_counts)
    t = spec_S1.livetime
    print(t)
    en_cps = [x / t for x in en_counts]
    print(en_cps)
    iso_br = sp.Sample4_24h.br
    iso_cps = []
    for i in range(len(iso_energy)):
        en = iso_energy[i]

        FWHM = ((2.355 * (0.09 * 0.00296 * en) ** 0.5) ** 2
                + (1.3) ** 2 ) ** 0.5 #keV
        start = en - .5 * FWHM
        end = en + .5 * FWHM

        val1 = (np.abs(back_spec_ener_spec - start)).argmin()
        val2 = (np.abs(back_spec_ener_spec - end)).argmin()

        back_vals = back_spec.cps_vals[val1:val2]

        total = sum(back_vals)
        print(total)
        new_count = en_cps[i] - total
        iso_cps.append(new_count)
        #return(iso_cps)
    isotope_activities = []
    for j in range(len(iso_name)):
        ef_en = (np.abs(ef.x - iso_energy[j])).argmin()
        activ = iso_cps[j] / (ef.fit[ef_en] * iso_br[j])
        isotope_activities.append(activ)
    return(iso_name, iso_energy, iso_cps, iso_br, isotope_activities)


lists = IsotopeActivity()
#print(lists)
iso_cps = lists[2]
iso_name = lists[0]
iso_energy = lists[1]
iso_br = lists[3]
isotope_activities = lists[4]
print(isotope_activities)

def Remover():
    for i in iso_cps:
        if i <= 0:
            n = iso_cps.index(i)
            iso_name.remove(iso_name[n])
            iso_energy.remove(iso_energy[n])
            iso_br.remove(iso_br[n])
            isotope_activities.remove(isotope_activities[n])
            iso_cps.remove(iso_cps[n])
        else:
            pass
    return(iso_name, iso_cps, iso_energy, iso_br, isotope_activities)

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
        irrad_quan = quantity.bq_at(irr_stop)
        irrad_act = IsotopeQuantity(nuclide, date=irr_stop, bq=irrad_quan)
        ni = NeutronIrradiation(irr_start, irr_stop, n_cm2_s=flux)
        init_comp = ni.activate(x_val, initial=Isotope(iso_2), activated=irrad_act)
        print(init_comp)
        #conc.extend[str(init_comp)]
    #return(conc)

u = Concentration()
print(u)
