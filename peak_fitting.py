#!/usr/bin/env python
"""
Provides PeakFitter class for fitting of gaussian peaks in 1D spectra.
"""

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.font_manager import FontProperties
from lmfit import models
import pandas as pd
import time
from collections import OrderedDict


__author__ = "Joseph Curtis"
__copyright__ = "None"
__credits__ = ["Mark Bandstra", "Ren Cooper", "Brian Plimley"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Joseph Curtis"
__email__ = "joseph.c.curtis@gmail.com"
__status__ = "Production"


FWHM_SIG_RATIO = 2.35482


class PeakFitter(object):

    def __init__(self, x, y, x_units, y_units, y_sig=None, verbosity=0, **kwargs):
        """
        args (converted to numpy arrays of floats):
            x = bincen (bincenters)
            x_units = `Channels` or `Energy (keV)`
            y = spec (best practice is counts/keV/s but then err could be
                      incorrectly calculated if not provided)
            y_units = `Counts` or `Counts / second` or 'Counts / keV' or 'Counts / second / keV'
            y_sig = spec uncertainty
        kwargs:
            roi
            det_type
            x_edges
            x_widths
        """
        self.verbosity = verbosity
        assert len(x) == len(y)
        self.set_x(x, x_units, **kwargs)
        self.reset_y_min_max()
        self.set_y(y, y_units, y_sig)
        self.set_detector(**kwargs)
        self.fit_peak(**kwargs)

    @classmethod
    def from_spectra(cls, x, y, x_units, y_units, y_sig=None, **kwargs):
        obj = cls(x, y, x_units=x_units, y_units=y_units, y_sig=y_sig,
                  **kwargs)
        return obj

    @classmethod
    def from_spectra_series(cls, spec, spec_sig, x_units, y_units, **kwargs):
        obj = cls(spec.index, spec.values, x_units=x_units, y_units=y_units,
                  y_sig=spec_sig.values, **kwargs)
        return obj

    def set_x(self, x, x_units, x_edges=None, x_widths=None, **kwargs):
        # Resetting globals
        self.x_edges = None
        self.x_widths = None
        # Setting x
        self.x = np.array(x, dtype=float)
        # Units!
        valid_x_units = ['Channels', 'Energy (keV)']
        assert x_units in valid_x_units, 'x_units: {} not in valid set: {}'.format(
            x_units, valid_x_units)
        self.x_units = x_units
        # Sanity checks!
        if x_edges is not None:
            assert isinstance(x_edges, np.ndarray), \
                'x_edges is a {}'.format(type(x_edges))
            assert len(x_edges) == len(self.x) + 1
            x_edges = x_edges.astype(float)
        if x_widths is not None:
            assert isinstance(x_widths, np.ndarray), \
                'x_widths is a {}'.format(type(x_widths))
            assert len(x_widths) == len(self.x)
            x_widths = x_widths.astype(float)
        # If only x given we must assume the bins are of equal spacing for
        # later normalization
        if (x_edges is None) and (x_widths is None):
            # All bin widths except the last
            binw = np.diff(self.x)
            # Check they are all the same
            assert np.all(np.abs(np.diff(binw)) < 1e-6), \
                'Non-uniform bins and no x_edges or x_widths provided'
            # Make bin width array based on first bin
            self.x_widths = np.ones_like(self.x, dtype=float) * binw[0]
            # Make those edges
            self.x_edges = np.concatenate([
                self.x - self.x_widths / 2.,
                self.x[-1:] + self.x_widths[-1] / 2.])
        # If only x_edges given use it to set the x_widths
        elif x_widths is None:
            self.x_edges = x_edges
            self.x_widths = np.diff(self.x_edges)
        # If only x_widths given use it to set the x_edges
        elif self.x_edges is None:
            self.x_widths = x_widths
            self.x_edges = np.concatenate([
                self.x - self.x_widths / 2.,
                self.x[-1:] + self.x_widths[-1] / 2.])
        # If both are given...
        else:
            # More sanity checks!
            assert np.all(np.abs(self.x - (x_edges[1:] - x_widths / 2.)) < 1e-6), \
                'Right edges minus half width is not equal to given center'
            assert np.all(np.abs(self.x - (x_edges[:-1] + x_widths / 2.)) < 1e-6), \
                'Left edges plus half width is not equal to given center'
            self.x_widths = x_widths
            self.x_edges = x_edges

    def set_y(self, y, y_units, y_sig):
        """
        Set spec y and uncertainty. If no unc given try to calculate unc.
        """
        self.y = np.array(y, dtype=float)
        # Units!
        valid_y_units = ['Counts', 'Counts / second', 'Counts / keV', 'Counts / second / keV']
        assert y_units in valid_y_units, 'y_units: {} not in valid set: {}'.format(
            y_units, valid_y_units)
        self.y_units = y_units
        if y_sig is None:
            if self.y_units == 'Counts':
                y_sig = np.sqrt(self.y)
            else:
                raise TypeError('y_units is not `Counts` so I cannot calculate uncertainty from y')
        assert len(y_sig) == len(self.y)
        self.y_sig = np.array(y_sig, dtype=float)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_y_sig(self):
        return self.y_sig

    def set_roi(self, roi):
        self.x_min = roi[0]
        self.x_max = roi[1]
        self.roi_slc = (self.x >= self.x_min) & (self.x < self.x_max)

    def get_x_roi(self):
        return self.x[self.roi_slc]

    def get_y_roi(self):
        y = self.y[self.roi_slc]
        self.track_y_min_max(y)
        return y

    def get_y_sig_roi(self):
        return self.y_sig[self.roi_slc]

    def get_x_widths_roi(self):
        return self.x_widths[self.roi_slc]

    def set_detector(self, det_type='NaI', **kwargs):
        self.det_type = det_type

    def guess_fwhm(self, xpeak):
        """
        Approx sigma for initial gauss width (could be improved)
        """
        if self.det_type == 'NaI':
            fwhm_guess = 0.08 * xpeak
        elif self.det_type == 'HPGe':
            fwhm_guess = 0.0025 * xpeak
        else:
            raise NotImplementedError('Detector type ({}) not recognized'.format(self.det_type))
        return fwhm_guess

    def guess_sigma(self, xpeak):
        return self.guess_fwhm(xpeak) / FWHM_SIG_RATIO

    def fit_peak(self, roi=None, xpeak=None, sigma_guess=None,
                 model_name='gauss-erf-const', **kwargs):
        """
        Main routine
        """
        # Exit if no roi
        if roi is None:
            self.fit = None
            self.model_name = None
        else:
            self.model_name = model_name
            # Start timer
            tic = time.time()
            # ---------
            # Setup ROI
            # ---------
            self.set_roi(roi)
            x = self.get_x_roi()
            y = self.get_y_roi()
            y_sig = self.get_y_sig_roi()
            x_widths = self.get_x_widths_roi()
            # ---------------------------
            # Guesses based on input data
            # ---------------------------
            # Set peak center to center of ROI if not given
            if xpeak is None:
                xpeak = (x[0] + x[-1]) / 2.
            # Guess sigma if not provided
            if sigma_guess is None:
                fwhm_guess = self.guess_fwhm(xpeak)
                sigma_guess = fwhm_guess / FWHM_SIG_RATIO
            # Heights at the sides of the ROI
            left_shelf_height = y[0]
            right_shelf_height = y[-1]
            # Line guess
            lin_slope = (y[-1] - y[0]) / (x[-1] - x[0])
            lin_intercept = y[0] - lin_slope * x[0]
            # Two peaks guess (33 and 66 percent through ROI)
            xpeak0 = x[0] + (x[-1] - x[0]) * 0.33
            xpeak1 = x[0] + (x[-1] - x[0]) * 0.66
            # Index of at the ROI center
            ix_half = int(round(float(len(x)) / 2.))
            # -------------------
            # Setup fitting model
            # -------------------
            if model_name == 'gauss-erf-const':
                # Models
                erf_mod = models.StepModel(form='erf', prefix='erf_')
                gauss_mod = models.GaussianModel(prefix='gauss_')
                bk_mod = models.ConstantModel(prefix='bk_')
                # Initialize parameters
                pars = erf_mod.make_params()
                pars.update(gauss_mod.make_params())
                pars.update(bk_mod.make_params())
                # Erfc (sigma and center are locked to gauss below)
                pars['erf_amplitude'].set(right_shelf_height - left_shelf_height, max=0.)
                # Gauss
                pars['gauss_center'].set(xpeak)  # , min=xpeak - 2 * fwhm_guess, max=xpeak + 2 * fwhm_guess)
                pars['gauss_sigma'].set(sigma_guess)
                pars['gauss_amplitude'].set(np.sum(y * x_widths), min=0)
                # Background
                pars['bk_c'].set(left_shelf_height, min=0.)
                # Same center and sigma
                pars.add('erf_center', expr='gauss_center')
                pars.add('erf_sigma', expr='gauss_sigma * {}'.format(FWHM_SIG_RATIO))
                self.model = gauss_mod + erf_mod + bk_mod
            elif model_name == 'double-gauss-line':
                # Models
                lin_mod = models.LinearModel(prefix='lin_')
                g0_mod = models.GaussianModel(prefix='gauss0_')
                g1_mod = models.GaussianModel(prefix='gauss1_')
                # Initialize parameters
                pars = lin_mod.make_params()
                pars.update(g0_mod.make_params())
                pars.update(g1_mod.make_params())
                # Line (background)
                pars['lin_slope'].set(lin_slope, max=0.)
                pars['lin_intercept'].set(lin_intercept)
                # Gauss 0 (left)
                pars['gauss0_center'].set(xpeak0)  # , min=xpeak - 2 * fwhm_guess, max=xpeak + 2 * fwhm_guess)
                pars['gauss0_sigma'].set(sigma_guess)
                pars['gauss0_amplitude'].set(np.sum(y[:ix_half] * x_widths[:ix_half]), min=0)
                # Gauss 1 (right)
                pars['gauss1_center'].set(xpeak1)  # , min=xpeak - 2 * fwhm_guess, max=xpeak + 2 * fwhm_guess)
                pars['gauss1_sigma'].set(sigma_guess)
                pars['gauss1_amplitude'].set(np.sum(y[ix_half:] * x_widths[ix_half:]), min=0)
                self.model = lin_mod + g0_mod + g1_mod
            else:
                raise NotImplementedError('Model ({}) not recognized'.format(model_name))
            # -----------
            # Perform fit
            # -----------
            try:
                self.fit = self.model.fit(y, pars, x=x, weights=1. / y_sig)
            except:
                print("[ERROR] Couldn't fit peak")
                self.fit = None
            if self.verbosity > 0:
                print('Fit time: {:.3f} seconds'.format(time.time() - tic))

    def get_x_from_fit(self):
        independent_var = self.fit.model.independent_vars[0]
        return self.fit.userkws[independent_var]

    def get_y_from_fit(self):
        return self.fit.data

    def get_y_sig_from_fit(self):
        return 1. / self.fit.weights

    def eval_init(self, x):
        """
        Evaluate init fit curve as `x`
        """
        return self.model.eval(x=x, **self.fit.init_values)

    def eval(self, x):
        """
        Evaluate best fit curve as `x`
        """
        return self.model.eval(x=x, **self.fit.best_values)

    def default_plot(self):
        if self.fit is not None:
            self.fit.plot()

    def reset_y_min_max(self):
        self.y_min = 0.
        self.y_max = 0.

    def track_y_min_max(self, y):
        """Always maintain y range +/- 5% of plotted ymin/ymax"""
        new_y_min = y.min() - abs(y.min() * 0.2)
        new_y_max = y.max() + abs(y.max() * 0.2)
        if new_y_min < self.y_min:
            self.y_min = new_y_min
        if new_y_max > self.y_max:
            self.y_max = new_y_max

    def custom_plot(self, title=None, savefname=None, **kwargs):
        self.reset_y_min_max()
        # Prepare plots
        gs = GridSpec(2, 2, height_ratios=(4, 1))
        gs.update(left=0.05, right=0.99, wspace=0.03, top=0.94, bottom=0.06,
                  hspace=0.06)
        fig = plt.figure(figsize=(18, 9))
        fit_ax = fig.add_subplot(gs[0, 0])
        res_ax = fig.add_subplot(gs[1, 0], sharex=fit_ax)
        txt_ax = fig.add_subplot(gs[:, 1])
        # Set fig title
        if title is not None:
            fig.suptitle(str(title), fontweight='bold', fontsize=24)
        # ---------------------------------------
        # Fit plot (keep track of min/max in roi)
        # ---------------------------------------
        # Smooth roi x values
        x_plot = np.linspace(self.x_min, self.x_max, 1000)
        # All data (not only roi)
        fit_ax.errorbar(self.get_x(), self.get_y(), yerr=self.get_y_sig(),
                        c='k', fmt='o', markersize=5, label='data')
        # Init fit
        y = self.eval_init(x_plot)
        self.track_y_min_max(y)
        fit_ax.plot(x_plot, y, 'k--', label='init')
        # Best fit
        y = self.eval(x_plot)
        self.track_y_min_max(y)
        fit_ax.plot(x_plot, y, color='#e31a1c', label='best fit')
        # Components (currently will work for <=3 component)
        colors = ['#1f78b4', '#33a02c', '#6a3d9a']
        for i, m in enumerate(self.fit.model.components):
            y = m.eval(x=x_plot, **self.fit.best_values)
            self.track_y_min_max(y)
            fit_ax.plot(x_plot, y, label=m.prefix, color=colors[i])
        # Plot Peak center and FWHM
        peak_centers = self.get_peak_center()
        peak_fwhm = self.get_peak_fwhm_absolute()
        for param, series in peak_centers.iterrows():
            fit_ax.axvline(series['value'], color='#ff7f00',
                           label=param + '_center')
            fit_ax.axvspan(series['value'] - peak_fwhm.loc[param, 'value'] / 2.,
                           series['value'] + peak_fwhm.loc[param, 'value'] / 2.,
                           color='#ff7f00', alpha=0.2, label=param + '_fwhm')
        # Misc
        fit_ax.legend(loc='upper right')
        fit_ax.set_ylabel(self.y_units)
        # Set viewing window to only include the roi (not entire spectrum)
        fit_ax.set_xlim([self.x_min, self.x_max])
        fit_ax.set_ylim([self.y_min, self.y_max])
        # ---------
        # Residuals
        # ---------
        res_ax.errorbar(self.get_x_from_fit(),
                        self.eval(self.get_x_from_fit()) - self.get_y_from_fit(),
                        yerr=self.get_y_sig_from_fit(), fmt='o', color='k',
                        markersize=5, label='residuals')
        res_ax.set_ylabel('Residuals')
        res_ax.set_xlabel(self.x_units)
        # -------------------
        # Fit report (txt_ax)
        # -------------------
        txt_ax.get_xaxis().set_visible(False)
        txt_ax.get_yaxis().set_visible(False)
        best_fit_values = ''
        op = self.fit.params
        for p in self.fit.params:
            best_fit_values += '{:15} {: .6e} +/- {:.5e} ({:6.1%})\n'.format(
                p, op[p].value, op[p].stderr, abs(op[p].stderr / op[p].value))
        best_fit_values += '{:15} {: .6e}\n'.format('Chi Squared:', self.fit.chisqr)
        best_fit_values += '{:15} {: .6e}'.format('Reduced Chi Sq:', self.fit.redchi)
        props = dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=1)
        props = dict(facecolor='white', edgecolor='none', alpha=0)
        fp = FontProperties(family='monospace', size=8)
        # Remove first 2 lines of fit report (long model description)
        s = '\n'.join(self.fit.fit_report().split('\n')[2:])
        # Add some more details
        s += '\n'
        peak_panel = self.get_peak_info_panel()
        for model_name in peak_panel.items:
            s += model_name + '\n'
            for param_name in peak_panel.major_axis:
                v = peak_panel.loc[model_name, param_name, 'value']
                e = peak_panel.loc[model_name, param_name, 'stderr']
                s += '    {:24}: {: .6e} +/- {:.5e} ({:6.1%})\n'.format(
                    param_name, v, e, e / v)
        # Add to empty axis
        txt_ax.text(x=0.01, y=0.99, s=s, fontproperties=fp,
                    ha='left', va='top', transform=txt_ax.transAxes,
                    bbox=props)
        if savefname is not None:
            fig.savefig(savefname)
            plt.close(fig)

    def get_param_value(self, param):
        return self.fit.params[param].value

    def get_param_sig(self, param):
        return self.fit.params[param].stderr

    def get_param_names_by_model_type(self, model_type, param):
        keys = []
        for k in self.fit.best_values.keys():
            if k.startswith(model_type) and k.endswith(param):
                keys.append(k)
        assert len(keys) > 0, 'No {} keys for {}: \n{}'.format(
            param, model_type, self.fit.best_values)
        return keys

    def get_params_by_model_type(self, model_type, param):
        param_values = OrderedDict([
            ('model', []),
            ('value', []),
            ('stderr', [])])
        for p in self.get_param_names_by_model_type(model_type, param):
            param_values['model'].append(p.split('_')[0])
            param_values['value'].append(self.get_param_value(p))
            param_values['stderr'].append(self.get_param_sig(p))
        param_values = pd.DataFrame(param_values)
        param_values = param_values.set_index('model')
        return param_values

    def get_peak_size(self):
        return self.get_params_by_model_type('gauss', 'amplitude')

    def get_peak_center(self):
        return self.get_params_by_model_type('gauss', 'center')

    def get_peak_fwhm_absolute(self):
        return self.get_params_by_model_type('gauss', 'sigma') * FWHM_SIG_RATIO

    def get_peak_fwhm_relative(self):
        f = self.get_peak_fwhm_absolute()
        c = self.get_peak_center()
        v = f['value'] / c['value']
        dv = v * np.sqrt(
            (f['stderr'] / f['value']) ** 2 + (c['stderr'] / c['value']) ** 2)
        out = v.to_frame(name='value')
        out['stderr'] = dv
        return out

    def get_peak_size_units(self):
        if self.y_units == 'Counts / second / keV':
            return 'cps'
        elif self.y_units == 'Counts / keV':
            return 'Counts'
        else:
            return 'unscaled'

    def get_peak_info_panel(self):
        pn = pd.Panel(OrderedDict([
            ('Peak Size ({})'.format(self.get_peak_size_units()), self.get_peak_size()),
            ('Peak Center ({})'.format(self.x_units), self.get_peak_center()),
            ('FWHM ({})'.format(self.x_units), self.get_peak_fwhm_absolute()),
            ('FWHM (ratio)', self.get_peak_fwhm_relative()),
        ]))
        pn = pn.swapaxes('items', 'major')
        return pn

    def get_peak_characteristics(self):
        pc = self.get_peak_center()
        pfa = self.get_peak_fwhm_absolute()
        pfr = self.get_peak_fwhm_relative()
        ps = self.get_peak_size()
        data = OrderedDict()
        for peak_name in pc.index:
            data[peak_name] = OrderedDict([
                ('Peak_Center_{}'.format(self.x_units), pc.loc[peak_name, 'value']),
                ('Peak_Center_{}_err'.format(self.x_units), pc.loc[peak_name, 'stderr']),
                ('Peak_FWHM_{}'.format(self.x_units), pfa.loc[peak_name, 'value']),
                ('Peak_FWHM_{}_err'.format(self.x_units), pfa.loc[peak_name, 'stderr']),
                ('Peak_FWHM_Ratio', pfr.loc[peak_name, 'value']),
                ('Peak_FWHM_Ratio_err', pfr.loc[peak_name, 'stderr']),
                ('Peak_Size_{}'.format(self.y_units), ps.loc[peak_name, 'value']),
                ('Peak_Size_{}_err'.format(self.y_units), ps.loc[peak_name, 'stderr']),
                ('Reduced_Chi_Squared', self.get_reduced_chi_squared()),
            ])
        return pd.DataFrame(data)

    def get_chi_squared(self):
        return self.fit.chisqr

    def get_reduced_chi_squared(self):
        return self.fit.redchi


if __name__ == "__main__":
    # Load sample spectra and energies
    df = pd.read_csv('fitting_test_spectra.csv', index_col=0)
    for c in ['source']:
        for kwargs in [{'roi': [550, 800], 'xpeak': 662, 'title': 'Cs137'},
                       {'roi': [1350, 1550], 'xpeak': 1460, 'title': 'K40'},
                       {'roi': [2450, 2850], 'xpeak': 2614, 'title': 'Tl208'}]:
            print(c)
            spec = df[c]
            spec_sig = df[c + '_sig']
            pf = PeakFitter.from_spectra_series(
                spec, spec_sig, x_units='Energy (keV)',
                y_units='Counts / second / keV', **kwargs)
            print('Peak Characteristics:')
            print(pf.get_peak_characteristics())
            pf.custom_plot(**kwargs)
    plt.show()
