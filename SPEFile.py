from __future__ import print_function
import numpy
from SpectrumFileBase import SpectrumFileBase


class SPEFile(SpectrumFileBase):

    """
    SPE ASCII file parser

    Basically, all you need is:
        SPEFile.read()
        SPEFile.calibrate()

    Then the data are in
        SPEFile.data [counts]
        SPEFile.channel
        SPEFile.energy
        SPEFile.energy_binwidth

    ORTEC's SPE file format is given on page 73 of this document:
        http://www.ortec-online.com/download/ortec-software-file-structure-manual.pdf

    Quoted here:

    The SPE format files are ASCII text files with several fields before and
    after the spectrum data. The fields are delimited by fixed keywords
    beginning with $ in column 1. The spectrum data is one channel per line.
    A program can read and use or ignore any fields or keywords not wanted or
    recognized. Blank lines are ignored. This format is used by several
    different groups for data interchange.

    $SPEC_ID:   One line of text describing the data
    $SPEC_REM:  Any number of lines containing remarks about the data
    $DATE_MEA:  Measurement date in the form mm/dd/yyyy hh:mm:ss
    $MEAS_TIM:  Live time and realtime of the spectrum in integer seconds,
                separated by spaces
    $DATA:      The first line contains the channel number of the first channel
                and the number of channels separated by spaces. The remaining
                lines contain one channel each of data.
    $ROI:       This group contains the regions of interest marked in the
                spectrum. The first line the number of regions, the following
                lines contain the start and stop channels for each region.
    $ENER_FIT:  This contains the energy calibration factors (a + b * chn) as
                two real numbers, separated by spaces.
    $MCA_CAL:   This contains the number of energy calibration factors on the
                first line, then the factors on the second line as two numbers,
                separated by spaces.
    $SHAPE_CAL: This contains the number of FWHM calibration factors on the
                first line, then the factors on the second line as two numbers,
                separated by spaces.

    Mark S. Bandstra
    Jan. 2014
    """

    def __init__(self, filename):
        super(SPEFile, self).__init__(filename)
        # SPE-specific
        self.ROIs = []
        self.energy_cal = []
        self.shape_cal = []

    def __str__(self, show_data=False):
        return self.str_spe(show_data=show_data)

    def str_spe(self, show_data=False):
        s = ''
        s += '$SPEC_ID:\n'
        s += self.spectrum_id + '\n'
        s += '$SPEC_REM:\n'
        s += self.sample_description + '\n'
        if self.collection_start is not None:
            s += '$DATE_MEA:\n'
            s += self.collection_start + '\n'
        s += '$MEAS_TIM:\n'
        s += '{:.0f} {:.0f}\n'.format(self.livetime, self.realtime)
        s += '$DATA:\n'
        s += '{:d} {:d}\n'.format(self.first_channel, self.num_channels)
        if show_data:
            for j in range(self.num_channels):
                s += '       {:d}\n'.format(self.data[j])
        s += '$ROI:\n'
        for line in self.ROIs:
            s += line + '\n'
        if len(self.energy_cal) > 0:
            s += '$ENER_FIT:\n'
            s += '{:f} {:f}\n'.format(self.energy_cal[0], self.energy_cal[1])
        if len(self.cal_coeff) > 0:
            s += '$MCA_CAL:\n'
            n_coeff = len(self.cal_coeff)
            s += '{:d}\n'.format(n_coeff)
            s += '{:E}'.format(self.cal_coeff[0])
            for j in range(1, n_coeff):
                s += ' {:E}'.format(self.cal_coeff[j])
            s += '\n'
        if len(self.shape_cal) > 0:
            s += '$SHAPE_CAL:\n'
            n_coeff = len(self.shape_cal)
            s += '{:d}\n'.format(n_coeff)
            s += '{:E}'.format(self.shape_cal[0])
            for j in range(1, n_coeff):
                s += ' {:E}'.format(self.shape_cal[j])
            s += '\n'
        return s

    def read(self, verbose=False):
        self.read_spe(verbose=verbose)

    def read_spe(self, verbose=False):
        print('SPEFile: attempting to read file ' + self.filename)
        assert(self.filename.split('.')[-1].upper() == 'SPE')
        with open(self.filename, 'r') as f:
            lines = f.readlines()
            # remove newlines from end of each line
            for i in range(len(lines)):
                lines[i] = lines[i].strip()
            i = 0
            while i < len(lines):
                # check whether we have reached a keyword and parse accordingly
                if lines[i] == '$SPEC_ID:':
                    i += 1
                    self.spectrum_id = lines[i]
                    if verbose:
                        print(self.spectrum_id)
                elif lines[i] == '$SPEC_REM:':
                    self.sample_description = ''
                    i += 1
                    while lines[i][0] != '$':
                        self.sample_description += lines[i] + '\n'
                        i += 1
                    i -= 1
                    if verbose:
                        print(self.sample_description)
                elif lines[i] == '$DATE_MEA:':
                    i += 1
                    self.collection_start = lines[i]
                    if verbose:
                        print(self.collection_start)
                elif lines[i] == '$MEAS_TIM:':
                    i += 1
                    self.livetime = float(lines[i].split(' ')[0])
                    self.realtime = float(lines[i].split(' ')[1])
                    if verbose:
                        print(self.livetime, self.realtime)
                elif lines[i] == '$DATA:':
                    i += 1
                    self.first_channel = int(lines[i].split(' ')[0])
                    # I don't know why it would be nonzero
                    assert(self.first_channel == 0)
                    self.num_channels = int(lines[i].split(' ')[1])
                    if verbose:
                        print(self.first_channel, self.num_channels)
                    j = self.first_channel
                    while j < self.num_channels + self.first_channel:
                        i += 1
                        self.data = numpy.append(self.data, int(lines[i]))
                        self.channel = numpy.append(self.channel, j)
                        j += 1
                elif lines[i] == '$ROI:':
                    self.ROIs = []
                    i += 1
                    while lines[i][0] != '$':
                        self.ROIs.append(lines[i])
                        i += 1
                    i -= 1
                    if verbose:
                        print(self.ROIs)
                elif lines[i] == '$ENER_FIT:':
                    i += 1
                    self.energy_cal.append(float(lines[i].split(' ')[0]))
                    self.energy_cal.append(float(lines[i].split(' ')[1]))
                    if verbose:
                        print(self.energy_cal)
                elif lines[i] == '$MCA_CAL:':
                    i += 1
                    n_coeff = int(lines[i])
                    i += 1
                    for j in range(n_coeff):
                        self.cal_coeff.append(float(lines[i].split(' ')[j]))
                    if verbose:
                        print(self.cal_coeff)
                elif lines[i] == '$SHAPE_CAL:':
                    i += 1
                    n_coeff = int(lines[i])
                    i += 1
                    for j in range(n_coeff):
                        self.shape_cal.append(float(lines[i].split(' ')[j]))
                    if verbose:
                        print(self.shape_cal)
                else:
                    print('Unknown line: ', lines[i])
                i += 1
        return True

    def write(self, filename):
        """Write back to a file."""
        self.write_spe(filename)

    def write_spe(self, filename):
        """Write back to a file."""
        with open(filename, 'w') as outfile:
            s = self.__str__(show_data=True)
            print(s, file=outfile)
        return True

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            print('Energy (keV),Counts,Counts Per Second', file=f)
            for e, d in zip(self.energy, self.data):
                print('{:},{:},{:}'.format(e, d, d/self.livetime) , file=f)

    def reduce_channels(self):
        """Combine every 2 bins, in case MCA resolution was too high."""
        num_channels_new = (self.num_channels + 1) / 2 - 1
        data_new = []
        for j in range(num_channels_new):
            data_new.append(self.data[2 * j:2 * j + 2].sum())
        self.num_channels = num_channels_new
        self.data = numpy.array(data_new)
        self.channel = numpy.arange(self.num_channels)
        for j in range(len(self.energy_cal)):
            self.energy_cal[j] *= pow(2., j)
        for j in range(len(self.cal_coeff)):
            self.cal_coeff[j] *= pow(2., j)
        for j in range(len(self.shape_cal)):
            self.shape_cal[j] *= pow(2., j)
        self.calibrate()


if __name__ == '__main__':
    import pylab
    import glob
    import os
    import sys

    if len(sys.argv) > 1:
        data_files =  sys.argv[1:]
    else:
        data_files = glob.glob('data/*.[Ss][Pp][Ee]')
    pylab.figure()
    for data_file in data_files:
        print('')
        print(data_file)
        spec = SPEFile(data_file)
        spec.read()
        spec.calibrate()
        print(spec)
        print(spec.livetime, 'seconds')
        print('Saving data to CSV file...')
        spec.write_csv(''.join(data_file.split('.')[0:-1]) + '.csv')
        # spec.write(data_file[:-4] + '_orig.Spe')
        # spec.reduce_channels()
        # spec.write(data_file[:-4] + '_reduced.Spe')
        pylab.semilogy(spec.energy,
                       spec.data / spec.energy_binwidth / spec.livetime,
                       label=data_file.split('/')[-1])
        pylab.xlabel('Energy (keV)')
        pylab.ylabel('Counts/keV/sec')
        pylab.ylim(1.e-5, 3.e1)
        pylab.xlim(0, 2800)
    pylab.legend()
    leg = pylab.gca().get_legend()
    ltext = leg.get_texts()
    pylab.setp(ltext, fontsize='small')
    pylab.show()
