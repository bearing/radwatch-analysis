"""
This will perform a gamma analysis
It will collect two spectra:
M = Measurement Spectrum
B = Background Spectrum
"""

from __future__ import print_function
from SpectrumFileBase import SpectrumFileBase
import SPEFile
import math
import numpy
import matplotlib.pyplot as plt

EFFICIENCY_CAL_COEFFS = [5.1164, 161.65, 3952.3, 30908]


def absolute_efficiency(energy, coeffs=EFFICIENCY_CAL_COEFFS):
    """
    Returns absolute efficiency for a given energy, based on a provided
    efficiency calibration.
    """

    efficiency = math.exp(coeffs[3]*(math.log(energy)/energy)**3 -
                          coeffs[2]*(math.log(energy)/energy)**2 +
                          coeffs[1]*(math.log(energy)/energy) - coeffs[0])

    return efficiency


def peak_measurement(M, energy):
    """
    Takes in a measured spectra alongside a specific energy and returns the net
    area and uncertainty for that energy.
    """
    energy_axis = M[0]
    M_counts = M[1]

    # Rough estimate of FWHM.
    FWHM = 0.05*energy**0.5

    # Peak Gross Area

    start_peak = 0
    while energy_axis[start_peak] < (energy - FWHM):
        start_peak += 1

    end_peak = start_peak
    while energy_axis[end_peak] < (energy + FWHM):
        end_peak += 1

    gross_counts_peak = sum(M_counts[start_peak:end_peak])

    # Left Gross Area

    left_peak = energy - 2*FWHM

    left_start = 0
    while energy_axis[left_start] < (left_peak - FWHM):
        left_start += 1

    left_end = left_start
    while energy_axis[left_end] < (left_peak + FWHM):
        left_end += 1

    gross_counts_left = sum(M_counts[left_start:left_end])

    # Right Gross Area

    right_peak = energy + 2*FWHM

    right_start = 0
    while energy_axis[right_start] < (right_peak - FWHM):
        right_start += 1

    right_end = right_start
    while energy_axis[right_end] < (right_peak + FWHM):
        right_end += 1

    gross_counts_right = sum(M_counts[right_start:right_end])

    # Net Area

    net_area = gross_counts_peak - (gross_counts_left + gross_counts_right)/2

    # Uncertainty

    uncertainty = (gross_counts_peak +
                   (gross_counts_left + gross_counts_right) / 4) ** 0.5

    # Returning results

    results = [net_area, uncertainty]

    return results


def Background_Subtract(M, B):
    """
    Background_Subtract will subtract the background spectrum
    from a given measurement. This will return the energy bins using a given
    energy calibration as well as the background subtracted counts of a
    measurement. Since both spectra come from the same detector, this assumes
    the energy calibrations are the same.
    """

    M_Counts = M.data
    B_Counts = B.data

    M_Time = M.livetime
    B_Time = B.livetime

    M_Channels = M.channel
    E0 = M.energy_cal[0]
    Eslope = M.energy_cal[1]

    Energy_Axis = B.channel
    Energy_Axis = Energy_Axis.astype(float)
    Energy_Axis[:] = [E0+Eslope*x for x in Channel]

    B_Counts_M = [1.0]*len(M.channel)

    B_Counts_M[:] = [x*(M_Time/B_Time) for x in B_Counts]

    M_Sub_Back = [1.0]*len(M_Channels)

    M_Sub_Back = [M_Counts[x]-B_Counts_M[x] for x in M.channel]

    Sub_Spect = [Energy_Axis, M_Sub_Back]

    return Sub_Spect


def main():
    Measurement = SPEFile.SPEFile()
    Background = SPEFile.SPEFile()

    Measurement.read()
    Background.read()

    Sub_Measurement = Background_Subtract(M=Measurement, B=Background)

if __name__ == '__main__':
    main()
