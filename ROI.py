from becquerel import Spectrum
import numpy as np
import matplotlib.pyplot as plt

#Input: Spec, Bg, E_Peak, side_bands(have a default)
#Method: set_sidebands, get_counts

class ROI(object):
	def __init__ (self, spec, bg, e_peak):
		self.spec = spec
		self.bg = bg
		self.target_peak = e_peak
		self.delta_E = 5
		self.window = np.array([[-2, -1], [-0.5, 0.5], [1, 2]])

	def set_sideband (self, delta_e, window):
		if (np.array(window).ndim != 2 or len(window) != 3):
			print ("Wrong input dimension.")
			return

		self.delta_E = delta_e
		self.window = np.array(window)

	def get_counts (self):
		bgsub = self.spec - self.bg
		idx = (bgsub.energies_kev > self.target_peak+self.window[0,0]*self.delta_E)*(bgsub.energies_kev < self.target_peak+self.window[0,1]*self.delta_E)
		prev_bins = np.where(idx)
		idx = (bgsub.energies_kev > self.target_peak+self.window[1,0]*self.delta_E)*(bgsub.energies_kev < self.target_peak+self.window[1,1]*self.delta_E)
		curr_bins = np.where(idx)
		idx = (bgsub.energies_kev > self.target_peak+self.window[2,0]*self.delta_E)*(bgsub.energies_kev < self.target_peak+self.window[2,1]*self.delta_E)
		post_bins = np.where(idx)
		counts_1 = np.sum(bgsub.cps_vals[prev_bins[0][0]:prev_bins[0][-1]]) * self.spec.livetime
		counts_2 = np.sum(bgsub.cps_vals[post_bins[0][0]:post_bins[0][-1]]) * self.spec.livetime
		counts_target = np.sum(bgsub.cps_vals[curr_bins[0][0]:curr_bins[0][-1]]) * self.spec.livetime
		background = (counts_1 + counts_2)/2
		net_counts = counts_target - background

		return net_counts
