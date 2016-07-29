from __future__ import print_function
import numpy
from scipy.interpolate import interp1d
import struct
import datetime


class SpectrumFileBase(object):

    """
    Spectrum file parser base class.

    Basically, all you need is:
        SpectrumFileBase.read()
        SpectrumFileBase.calibrate()

    Then the data are in
        SpectrumFileBase.data [counts]
        SpectrumFileBase.channel
        SpectrumFileBase.energy
        SpectrumFileBase.energy_binwidth

    Mark S. Bandstra
    Jan. 2014
    """

    def __init__(self, filename):
        super(SpectrumFileBase, self).__init__()
        self.filename = filename
        # to read from file
        self.spectrum_id = ''
        self.sample_description = ''
        self.detector_description = ''
        self.location_description = ''
        self.hardware_status = ''
        self.collection_start = None
        self.collection_stop = None
        self.realtime = 0.
        self.livetime = 0.
        self.first_channel = 0
        self.num_channels = 0
        # arrays to be read
        self.channel = numpy.array([], dtype=numpy.int32)
        self.data = numpy.array([], dtype=numpy.int32)
        self.cal_coeff = []
        # arrays to be calculated
        self.energy = numpy.array([], dtype=numpy.float)
        self.energy_binwidth = numpy.array([], dtype=numpy.float)

    def __str__(self, show_data=False):
        s = ''
        return s

    def read(self, verbose=False):
        """Read in the file."""
        self.cal_coeff = [0., 1.]
        return True

    def write(self, filename):
        """Write back to a file."""
        return True

    def calibrate(self):
        """Calculate energies corresponding to channels."""
        self.energy = self.channel_to_energy(self.channel)
        self.energy_binwidth = self.bin_width(self.channel)
        return True

    def channel_to_energy(self, channel):
        """Apply energy calibration to the given channel (or numpy array of
        channels)."""
        chan = numpy.float64(channel)
        en = numpy.zeros_like(chan)
        for j in range(len(self.cal_coeff)):
            en += self.cal_coeff[j] * pow(chan, j)
        return en

    def energy_to_channel(self, energy):
        """Invert the energy calibration to find the channel equivalent."""
        return interp1d(self.energy, self.channel)(energy)

    def bin_width(self, channel):
        """Calculate the width in keV of the bin at the given channel."""
        en0 = self.channel_to_energy(channel - 0.5)
        en1 = self.channel_to_energy(channel + 0.5)
        return en1 - en0


if __name__ == '__main__':

    spec = SpectrumFileBase('')
    spec.read()
    spec.calibrate()
    print(spec)
    spec.write('test.txt')
