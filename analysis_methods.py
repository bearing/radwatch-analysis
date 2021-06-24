import becquerel as bq
from becquerel import Spectrum
from becquerel.tools.isotope import Isotope
from becquerel.tools.isotope_qty import IsotopeQuantity, NeutronIrradiation
import numpy as np
import scipy.integrate as integrate
import math as m
import importlib
import pandas as pd
import sys
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import csv
from bs4 import BeautifulSoup
import urllib.request
import PF
import re
import json

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
        self.werr = []
        self.space = np.linspace(1, 2460, 540)
        self.z = []
        self.fit = []
        self.new_fit = []
        self.fit_lower = []
        self.fit_upper = []

    def mutate(self):
        """
        Mutates data and creates the fit function.
        """
        if len(self.unc)>0:
            if len(self.energy) != len(self.unc):
                print("Error: cannot perform fit without the same number of input energies, efficiencies, and uncertainties!")
                return
            for i in range(len(self.energy)): 
                self.x.append(np.log(self.energy[i]/1461))
                self.y.append(np.log(self.values[i]))
                #log_err = .5*(np.log(self.values[i]+self.unc[i])-np.log(self.values[i]-self.unc[i]))
                log_err = self.unc[i]/self.values[i]
                self.werr.append(1/log_err)

            self.z, self.z_cov = np.polyfit(np.asarray(self.x), np.asarray(self.y), 4, cov=True)
            print("Poly fit parameters: ",self.z)
            print("Poly fit covariance: ",self.z_cov)
        else:
            print("Error: cannot perform fit without input energies, efficiencies, and uncertainties!")

    def save_fit(self,filename='eff_calibration_parameters.json'):
        par_dict = {
            "parameters": self.z.tolist(),
            "covariance": self.z_cov.tolist(),
            "efficiencies": self.values,
            "uncertainties": self.unc
        }
        with open(filename, 'w') as file:
            json.dump(par_dict, file)

    def set_parameters(self,filename='eff_calibration_parameters.json'):
        file = open(filename, 'r')

        data = json.load(file)
        self.z = np.array(data['parameters'])
        self.z_cov = np.array(data['covariance'])
        self.values = data['efficiencies']
        self.unc = data['uncertainties']
        print("Loaded fit parameters 0-4:", self.z)
        print("Loaded fit uncertainties:", self.z_cov)
        print("Loaded input energies:", self.values)
        print("Loaded eff uncertainties:", self.unc)
        if len(self.z) != 5:
            print('ERROR: file does not contain the correct number of paramters (5)')

    def normal(self, x): 
        return np.log(x/1461)

    def func3(self, x): 
        func_value = (self.z[0]*self.normal(x)**4)+\
                     (self.z[1]*self.normal(x)**3)+\
                     (self.z[2]*self.normal(x)**2)+\
                     (self.z[3]*self.normal(x))+\
                     (self.z[4])
        return func_value

    def func3_error(self, x, side):
        # generate sample of possible parameter values based on the covariance matrix from the fit
        sample_par = np.random.multivariate_normal(mean=self.z.reshape(len(self.z),), cov=self.z_cov, size=1000)
        sample_z = np.transpose(sample_par)
        # We can now calculate the range of function values at a given x based on the sample of parameter values
        func_values = (sample_z[0]*self.normal(x)**4)+\
                      (sample_z[1]*self.normal(x)**3)+\
                      (sample_z[2]*self.normal(x)**2)+\
                      (sample_z[3]*self.normal(x))+\
                      (sample_z[4])
        # 1-sigma upper and lower bounds on the function value given assuming a gaussian distribution
        if side==0:
            return np.mean(func_values)+np.std(func_values)
        else:
            return np.mean(func_values)-np.std(func_values)

    def new_func(self, x): 
        return np.exp(self.func3(x))

    def new_func_upper(self, x):
        return np.exp(self.func3_error(x, 0))

    def new_func_lower(self, x):
        return np.exp(self.func3_error(x, 1))

    def new_func_error(self, x):
        error = np.abs(self.new_func_upper(x) - self.new_func_lower(x))/2.0
        return error

    def fitting(self):
        """
        Fits the data.
        """
        for i in self.space:
            self.fit.append(self.func3(i))
            self.new_fit.append(self.new_func(i))
            self.fit_upper.append(self.new_func_upper(i))
            self.fit_lower.append(self.new_func_lower(i))

    def get_eff(self,energy):
        return self.new_func(energy)

    def get_eff_error(self,energy):
        return self.new_func_error(energy)

    def plotter_pretty(self,ylim=None):
        fig = go.Figure([
            go.Scatter(
                name='Measurements',
                x=self.energy,
                y=self.values,
                mode='markers',
                error_y=dict(
                    type='data', # value of error bar given in data coordinates
                    array=self.unc,
                    visible=True)
            ),
            go.Scatter(
                name='Fitted Curve',
                x=self.space,
                y=self.new_fit,
                mode='lines',
                line=dict(color='rgb(31, 119, 180)'),
            ),
            go.Scatter(
                name='Upper Bound',
                x=self.space,
                y=self.fit_upper,
                mode='lines',
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False
            ),
            go.Scatter(
                name='Lower Bound',
                x=self.space,
                y=self.fit_lower,
                marker=dict(color="#444"),
                line=dict(width=0),
                mode='lines',
                fillcolor='rgba(68, 68, 68, 0.3)',
                fill='tonexty',
                showlegend=False
            )
        ])
        fig.update_layout(
            xaxis_title='Energy [keV]',
            yaxis_title='Efficiency',
            title='Efficiency Curve',
            hovermode="x"
        )
        plot_color = 'plotly_white'
        text_color = 'black'
        if ylim:
            fig.update_yaxes(range=[-0.002, ylim])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                          template=plot_color)
        fig.update_yaxes(showgrid=True,
                         gridcolor='gray',
                         linecolor=text_color,
                         tickcolor=text_color,
                        )
        fig.update_xaxes(gridcolor='gray',
                         linecolor=text_color,
                         tickcolor=text_color,
                        )
        fig.write_image("eff_curve.pdf")
        fig.show()

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
        plt.plot(self.space, self.fit_upper, '--')
        plt.plot(self.space, self.fit_lower, '--')
        plt.legend(('Data Points', 'Fitted Curve'), loc='upper right')
        if ylim is not None:
            plt.ylim(0, ylim)
        plt.savefig('eff_curve.png',dpi=200)
        plt.show()


    #input spectra and energy calibration

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

def xsec_data(abb, A_0):
    '''extracts data from the jaea website'''
    bslink = urlcreator(abb, A_0)

    table = bslink.table
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]

        if len(row) == 8:
            if row[1] == '(n,γ) ':
                x_sec = row[2]
                x_sec_s = x_sec.split(' ')
                x_val = float(x_sec_s[0])
                barn = x_sec_s[1]
                if barn[1] == '(kb)':
                    x_val = 10**(3) * x_val
                    return x_val
                elif barn[1] == '(mb)':
                    x_val = 10**(-3) * x_val
                    return x_val
                elif barn[1] == '(μb)':
                    x_val = 10**(-6) * x_val
                    return x_val
                elif barn[1] == '(nb)':
                    x_val = 10**(-9) * x_val
                    return x_val
                else:
                    x_val = x_val
                    return x_val

            else:
                pass

        else:
            pass
    return None

def get_initial_isotopes(isotopes):
    init_isotopes = []
    for iso in isotopes:
        iso_name = re.findall("[a-zA-Z]+",iso)[0]
        if(len(iso_name)>1):
            iso_name = iso_name[0] + iso_name[1].lower()
        iso_A = int(re.findall("[0-9]+",iso)[0])
        iso_A0 = iso_A - 1
        init_isotopes.append(iso_name+'-'+str(iso_A0))
    return init_isotopes

def calculate_concentration(dataframes,name_in,name_out,flux,irr_start,irr_stop,specs):
    for ispec,df in enumerate(dataframes):
        concentrations = []
        for i in range(len(df['isotopes'])):
            iso_name = re.findall("[a-zA-Z]+",df['isotopes'].iloc[i])[0]
            if(len(iso_name)>1):
                iso_name = iso_name[0] + iso_name[1].lower()
            iso_A = int(re.findall("[0-9]+",df['isotopes'].iloc[i])[0])
            iso_A0 = iso_A - 1

            x_val = xsec_data(iso_name, iso_A0)

            nuclide = Isotope(df['isotopes'].iloc[i])
            initial = Isotope(iso_name+str(iso_A0))

            isotope = IsotopeQuantity(nuclide, date=specs[ispec].start_time, bq=df[name_in].iloc[i])
            ni = NeutronIrradiation(irr_start, irr_stop, n_cm2_s=flux)
            init_comp = ni.activate(x_val, initial=initial, activated=isotope)

            concentrations.append(init_comp.g_at(irr_start))
        df[name_out] = concentrations
    return dataframes

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
