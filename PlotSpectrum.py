import SpectrumFile
import numpy as np
import matplotlib.pyplot as plt


def plot_spectrum(spec, ax=None, **kwargs):
    """
    Plot the spectrum, spec (a SpectrumFile object).

    If ax is specified, plot it on that axes.
    Other **kwargs are passed to plt.semilogy.
    """

    if not spec.data.size or not spec.energy.size or np.all(spec.energy == 0):
        raise ValueError('Spectrum must be loaded and calibrated')

    ax = plot_xy(spec.energy, spec.data, ax=ax, **kwargs)

    return ax


def plot_uncal_spectrum(spec, ax=None, **kwargs):
    """
    Plot a spectrum vs. channel instead of energy.
    spec is a SpectrumFile object.
    """

    if not spec.data.size or not spec.channel.size:
        raise ValueError('Spectrum must be loaded')

    ax = plot_xy(spec.channel, spec.data, ax=ax, xlabel='Channel #', **kwargs)

    return ax


def plot_xy(x, y, ax=None, xlabel='Energy [keV]', **kwargs):
    """
    Plot x and y as a spectrum.
    """

    if not ax:
        new_plot = True
        plt.figure()
        ax = plt.axes()
    else:
        new_plot = False

    plt.semilogy(x, y, axes=ax, drawstyle='steps-mid', **kwargs)

    if new_plot:
        plt.xlabel(xlabel)
        plt.ylabel('Counts')

    if 'label' in kwargs:
        plt.legend()
    plt.show()

    return ax
