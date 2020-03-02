from becquerel import Spectrum
import numpy as np
import matplotlib.pyplot as plt

#Input: Spec, Bg, E_Peak, side_bands(have a default)
#Method: set_sidebands, get_counts

class ROI(object):
	def __init__ (self, spec, bg, e_peaks):
		self.spec = spec
		self.bg = bg
		self.bgsub = self.spec - self.bg
		self.target_peaks = e_peaks
		self.delta_E = 5
		self.window = np.array([[-2, -1], [-0.5, 0.5], [1, 2]])

	def set_sideband (self, delta_e, window):
		if (np.array(window).ndim != 2 or len(window) != 3):
			print ("Wrong input dimension.")
			return

		self.delta_E = delta_e
		self.window = np.array(window)

	def find_peak_energies (self):
		for i, target_peak in enumerate(self.target_peaks):
			idx = (self.bgsub.energies_kev > target_peak+self.window[1,0]*self.delta_E)*(self.bgsub.energies_kev < target_peak+self.window[1,1]*self.delta_E)
			bins = np.where(idx)
			local_idx = np.argmax(self.bgsub.cps_vals[bins])
			index = bins[0][0] + local_idx
			self.target_peaks[i] = self.bgsub.energies_kev[index]

	def get_roi_windows(self, target_peak):
		idx = (self.bgsub.energies_kev > target_peak+self.window[0,0]*self.delta_E)*(self.bgsub.energies_kev < target_peak+self.window[0,1]*self.delta_E)
		prev_bins = np.where(idx)
		idx = (self.bgsub.energies_kev > target_peak+self.window[1,0]*self.delta_E)*(self.bgsub.energies_kev < target_peak+self.window[1,1]*self.delta_E)
		curr_bins = np.where(idx)
		idx = (self.bgsub.energies_kev > target_peak+self.window[2,0]*self.delta_E)*(self.bgsub.energies_kev < target_peak+self.window[2,1]*self.delta_E)
		post_bins = np.where(idx)
		return 	prev_bins,curr_bins,post_bins

	def get_counts (self):
		net_counts = []
		for target_peak in self.target_peaks:
			prev_bins, curr_bins, post_bins = self.get_roi_windows(target_peak)
			counts_1 = np.sum(self.bgsub.cps_vals[prev_bins[0][0]:prev_bins[0][-1]]) * self.spec.livetime
			counts_2 = np.sum(self.bgsub.cps_vals[post_bins[0][0]:post_bins[0][-1]]) * self.spec.livetime
			counts_target = np.sum(self.bgsub.cps_vals[curr_bins[0][0]:curr_bins[0][-1]]) * self.spec.livetime
			background = (counts_1 + counts_2)/2
			inet_counts = counts_target - background
			net_counts.append(inet_counts)

		return net_counts
