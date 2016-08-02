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


def absolute_efficiency(energy):
    """
    Returns absolute efficiency for a given energy, based on a provided
    energy calibration.
    """

    efficiency = math.exp(30908*(math.log(energy)/energy)**3 - 3952.3*(math.log(energy)/energy)**2 + 161.65*(math.log(energy)/energy) - 5.1164)

    return efficiency


def Background_Subtract(M, B):
    """
    Background_Subtract will subtract the background spectrum
    from a given measurement. This will return the energy bins using a given
    energy calibration as well as the background subtracted counts of a
    measurement. Since both spectra come from the same detector, this assumes
    the energy calibrations are the same.
    """

    M_Counts                = M.data
    B_Counts                = B.data

    M_Time                  = M.livetime
    B_Time                  = B.livetime

    M_Channels              = M.channel
    E0                      = M.energy_cal[0]
    Eslope                  = M.energy_cal[1]

    Energy_Axis             = B.channel
    Energy_Axis             = Energy_Axis.astype(float)
    Energy_Axis[:]          = [E0+Eslope*x for x in Channel]

    B_Counts_M              = [1.0]*len(M.channel)

    B_Counts_M[:]           = [x*(M_Time/B_Time) for x in B_Counts]

    M_Sub_Back              = [1.0]*len(M_Channels)

    M_Sub_Back              = [M_Counts[x]-B_Counts_M[x] for x in M.channel]

    Sub_Spect = [Energy_Axis, M_Sub_Back]

    return Sub_Spect


def main():
    Measurement    = SPEFile.SPEFile()
    Background     = SPEFile.SPEFile()

    Measurement.read()
    Background.read()

    Sub_Measurement = Background_Subtract(M=Measurement, B=Background)

if __name__ == '__main__':
    main()
