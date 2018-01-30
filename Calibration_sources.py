import numpy as np
"""class that contains data for multiple sources used for calibration"""

"""Common sources include Co-60, Eu-152, Ir-194, Am-241"""

class Calibration(object):
    ca_isotopes = []
    def __init__(self, Symbol, A, Peak, Intensity, init_act, date):
        self.Symbol = Symbol
        self.A = A
        self.Peak = Peak
        self.Intensity = Intensity
        self.init_act = init_act #units in uCi
        self.date = date
        Calibration.ca_isotopes.append(self)

    def __repr__(self):
        return '{0}_{1}'.format(self.Symbol, self.A)


Na_22_peaks = {'Energy': [1274.54], 'Intensity': [0.9994]}

Na_22 = Calibration('Na', 22, Na_22_peaks['Energy'], Na_22_peaks['Intensity'], 1, '2009-03-12')

Mn_54_peaks = {'Energy': [834.85], 'Intensity': [0.9998]}

Mn_54 = Calibration('Mn', 54, Mn_54_peaks['Energy'], Mn_54_peaks['Intensity'], 9.031, '2008-01-15')

Co_57_peaks = {'Energy': [122.06, 136.47], 'Intensity': [0.856, 0.1068]}

Co_57 = Calibration('Co', 57, Co_57_peaks['Energy'], Co_57_peaks['Intensity'], 11.21, '2008-01-15')

Co_60_peaks = {'Energy': [1173.23, 1332.49], 'Intensity': [0.9985, 0.9998]}

Co_60 = Calibration('Co', 60, Co_60_peaks['Energy'], Co_60_peaks['Intensity'], 9.384, '2008-01-15')

Cd_109_peaks = {'Energy': [88], 'Intensity': [0.0364]}

Cd_109 = Calibration('Cd', 109, Cd_109_peaks['Energy'], Cd_109_peaks['Intensity'], 10.3, '2008-01-15')

Eu_152_peaks = {'Energy': [121.78, 244.7, 443.96, 867.38, 964.06, 1085.84, 1112.08, 1408.01],
                'Intensity': [0.2853, 0.076, 0.0283, 0.0423, 0.1451, 0.1011, 0.1367, 0.2087]}

Eu_152 = Calibration('Eu', 152, Eu_152_peaks['Energy'], Eu_152_peaks['Intensity'], 1.064, '2009-01-15')

Th_228_peaks = {'Energy': [84.373],
                'Intensity': [0.0122]}

Th_228 = Calibration('Th', 228, Th_228_peaks['Energy'], Th_228_peaks['Intensity'], 10.15, '2010-06-01')

#Th_232_peaks = {'Energy': [140.88], 'Intensity': [0.00021]}

#Th_232 = Calibration('Th', 232, Th_232_peaks['Energy'], Th_232_peaks['Intensity'])
