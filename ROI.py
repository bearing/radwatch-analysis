from becquerel import Spectrum
import numpy as np
import matplotlib.pyplot as plt
import math as m

#Input: Spec, Bg, E_Peak, side_bands(have a default)
#Method: set_sidebands, get_counts

class ROI(object):
    def __init__ (self, spec, bg, e_peaks, sub_type):
        #This function initiates an ROI object that requires a foreground and background spectrum, a list of energy peaks that is to be observed [keV], and a subtype of either 0 (background is not subtracted before applying ROI) or 1 (for spectra without double peaking).
        #When initiated, the ROI object will come with a dictionary of default parameters for each energy peak with the following indicies: key = initial peak energy, 0 = calibrated peak energy, 1 = delta e, 2 = foreground roi windows, 3 = bg roi windows
        self.spec = spec
        self.bg = bg
        self.sub_type = sub_type
        if sub_type == 0:
            self.bgsub = self.spec
        else:
            self.bgsub = self.spec - self.bg
        self.target_peaks = e_peaks
        self.roi_pars = {}
        for i in range(len(self.target_peaks)):
            self.roi_pars["%s" %self.target_peaks[i]] = [self.target_peaks[i], 5, [[-2, -1], [-0.5, 0.5], [1, 2]],[[-2, -1], [-0.5, 0.5], [1, 2]]]

    def set_sideband(self, peak_energy, delta_e, window, spec_type=0):
        #This function sets the window and sidebands around a peak energy defined by the user, telling the computer to consider each defined interval on the spectrum as peak counts or background counts.
        #peak_energy is the energy at which you're changing the sideband parameters to [keV].
        #delta_e is the amount of energy multiplied to the intervals defined in the window, giving the energy intervals. Use this to quickly expand or shrink the sidebands and window proportionally [keV].
        #window sets the intervals relative to delta_e. Use this to fine tune around regions of interest on the spectrum.
        #Example: roi.set_sideband(609, 5, [[-2, -1], [-0.75, 0.75], [1, 2]], 0)
        assert type(peak_energy) == int or type(peak_energy) == float, "First argument should be the value of the target peak that you want to set sidebands for."
        assert type(delta_e) == int or type(delta_e) == float, "Second argument should be a number designating delta_E."
        assert len(window) == 3 and len(window[0]) == 2 and len(window[1]) == 2 and len(window[2]) == 2, "Third argument should be a list of lists designating the window in the format of: [[#, #], [#, #], [#, #]]"
        assert f'{peak_energy}' in self.roi_pars, f"Set Sideband: {peak_energy} energy peak not found in ROI energies list"

        self.roi_pars["%s" %peak_energy][1] = delta_e
        if spec_type == 0:
            self.roi_pars["%s" %peak_energy][2] = window
        if spec_type == 1:
            self.roi_pars["%s" %peak_energy][3] = window

    def find_peak_energies(self, low=609, high=2614):
        #This function changes the peak energy value to better center the roi window around where the peak visually appears to be.
        #Assumes there's a predominant signal at 609keV and 2614keV.
        #Other low and high peaks may be substituted as the second and third argument respectively [keV].
            
        masklow = (self.spec.bin_centers_kev > (low - 15)) & (self.spec.bin_centers_kev < (low + 15))
        maxbinlow = np.argmax(self.spec.counts[masklow])
        maskhigh = (self.spec.bin_centers_kev > (high - 15)) & (self.spec.bin_centers_kev < (high + 15))
        maxbinhigh = np.argmax(self.spec.counts[maskhigh])
            
        dElow = low - self.spec.bin_centers_kev[np.where(masklow)[0][0] + maxbinlow]
        dEhigh = high - self.spec.bin_centers_kev[np.where(maskhigh)[0][0] + maxbinhigh]

        E_scale = (dEhigh - dElow) / (high - low) #m
        E_shift = dEhigh - high * E_scale #b
            
        new_peak_energy = lambda E: int(E) - (E_shift + (E_scale * int(E)))
        for peak_energy in self.roi_pars:
            self.roi_pars[f'{peak_energy}'][0] = int(round(new_peak_energy(peak_energy)))
            print(str(peak_energy) + "keV peak changed to " + str(int(round(new_peak_energy(peak_energy)))) + "keV")

    def get_roi_windows(self, key, spec_type=0):
        index = []
        if spec_type==0:
            for i in range(3):
                index.append(np.where((self.bgsub.bin_centers_kev > key[0]+key[2][i][0]*key[1])*(self.bgsub.bin_centers_kev <= key[0]+key[2][i][1]*key[1])))
        if spec_type==1:
            for i in range(3):
                index.append(np.where((self.bg.bin_centers_kev > key[0]+key[3][i][0]*key[1])*(self.bg.bin_centers_kev <= key[0]+key[3][i][1]*key[1])))
        return index

    def get_counts(self):
        #This function gives the counts and the uncertainty in [Bq].
        net_counts = []
        uncertainties = []
        for key in self.roi_pars:
            if self.sub_type == 1:
                bins = self.get_roi_windows(self.roi_pars[key])
                counts = []
                bin_range = []
                for i in range(len(bins)):
                    counts.append(np.sum(self.bgsub.cps_vals[bins[i][0][0]:bins[i][0][-1]]) * self.spec.livetime)
                    bin_range.append(bins[i][0][-1]-bins[i][0][0])
                # bg is the per-bin average background level determined from averaging the two side-band roi average bin values
                #  scaled by the number of peak bins
                bg = bin_range[1]*(counts[0]/bin_range[0] + counts[2]/bin_range[2])/2
                net_counts.append(counts[1] - bg)
                print("Peak counts at", self.roi_pars[key][0], "keV:", counts[1])
                print("Background counts:", self.roi_pars[key][0], "keV:", bg)

            else:
                bins = self.get_roi_windows(self.roi_pars[key], 1)
                bgcounts = []
                bg_bin_range = []
                for i in range(len(bins)):
                    bgcounts.append(np.sum(self.bg.cps_vals[bins[i][0][0]:bins[i][0][-1]]) * self.spec.livetime)
                    bg_bin_range.append(bins[i][0][-1]-bins[i][0][0])
                backgroundbg = bg_bin_range[1]*(bgcounts[0]/bg_bin_range[0] + bgcounts[2]/bg_bin_range[2]) / 2
                inet_countsbg = bgcounts[1] - backgroundbg
                print('background spec sidebands', backgroundbg)
                print('bg peak counts',bgcounts[1])

                speccounts = []
                spec_bin_range = []
                bins = self.get_roi_windows(self.roi_pars[key], 0)
                for i in range(len(bins)):
                    speccounts.append(np.sum(self.spec.cps_vals[bins[i][0][0]:bins[i][0][-1]]) * self.spec.livetime)
                    spec_bin_range.append(bins[i][0][-1]-bins[i][0][0])
                backgroundspec = spec_bin_range[1]*(speccounts[0]/spec_bin_range[0] + speccounts[2]/spec_bin_range[2]) / 2
                inet_counts = (speccounts[1] - backgroundspec) - inet_countsbg
                net_counts.append(inet_counts)
                print("signal bg", backgroundspec)
                print("signal peak", speccounts[1])

            unccounts = [[], []]
            #[[tot_speclow, counts_target_gross, tot_spechigh], [tot_bglow, counts_bg_gross, tot_bghigh]]
            for i in range(len(bins)):
                unccounts[0].append(np.sum(self.spec.cps_vals[bins[i][0][0]:bins[i][0][-1]]) * self.spec.livetime)
                unccounts[1].append(np.sum(self.bg.cps_vals[bins[i][0][0]:bins[i][0][-1]]) * self.spec.livetime)
            s_target_gross = (unccounts[0][1]) ** 0.5
            s_ROI_spec = ((unccounts[0][2] + unccounts[0][0]) ** 0.5) / 2
            s_bg_gross = (unccounts[1][1]) ** 0.5
            s_ROI_bg = ((unccounts[1][2] + unccounts[1][0]) ** 0.5) / 2
            s = (s_target_gross**2 + s_ROI_spec**2 + s_bg_gross**2 + s_ROI_bg**2) ** 0.5
            uncertainties.append(s)

        return net_counts,uncertainties

    def f_near(self, a, a0):
        idx = np.abs(a-a0).argmin()
        return idx

    def plot_peak_region(self, key, spec_type=0):
        assert f'{key}' in self.roi_pars, f"Plot Peak Region: {key} energy peak not found in ROI energies list"
        target_peaks = self.target_peaks
        counts = self.spec.counts_vals
        energies = self.spec.bin_centers_kev
        idx = self.f_near(energies,key)
        roi_low = idx - 50
        roi_high = idx + 50

        plot_counts = counts[roi_low:roi_high]
        plot_energies = energies[roi_low:roi_high]

        roi_low_bins,roi_peak_bins,roi_high_bins = self.get_roi_windows(self.roi_pars[f'{key}'],spec_type)
        rlow = roi_low_bins[0][0]
        rhi = roi_high_bins[0][-1]
        plot_counts = counts[rlow:rhi]
        plot_energies = energies[rlow:rhi]

        rlow = roi_low_bins[0][0]
        rhi = roi_low_bins[0][-1]
        low_counts = counts[rlow:rhi]
        low_energies = energies[rlow:rhi]

        rlow = roi_high_bins[0][0]
        rhi = roi_high_bins[0][-1]
        high_counts = counts[rlow:rhi]
        high_energies = energies[rlow:rhi]

        rlow = roi_peak_bins[0][0]
        rhi = roi_peak_bins[0][-1]
        peak_counts = counts[rlow:rhi]
        peak_energies = energies[rlow:rhi]

        fig,ax = plt.subplots()
        ax.plot(plot_energies,plot_counts)
        ax.fill_between(low_energies,0,low_counts,facecolor = 'green',interpolate=True)
        ax.fill_between(high_energies,0,high_counts,facecolor = 'red',interpolate=True)
        ax.fill_between(peak_energies,0,peak_counts,facecolor = 'blue',interpolate=True)
        ax.set_yscale('log')
        plt.title("%s Peak" %key)
