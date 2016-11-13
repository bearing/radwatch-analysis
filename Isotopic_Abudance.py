"""Isotopic Abundances for each isotope"""


class Natural_Isotope(object):
    def __init__(self, symbol, mass_number, mass, isotopic_abundance,
                 cross_section):
        self.symbol = symbol
        self.mass_number = mass_number
        self.mass = mass
        self.isotopic_abundance = .01 * isotopic_abundance
        self.cross_section = cross_section

Hydrogen_1 = Natural_Isotope("H", 1, 1.007825, 99.9885, 0.332015)
Hydrogen_2 = Natural_Isotope("H", 2, 2.014102, 0.0115, 0.000505706)
Helium_3 = Natural_Isotope("He", 3, 3.016029, 0.000137, 5.49873e-05)
Helium_4 = Natural_Isotope("He", 4, 4.002603, 99.999893, 0)
Lithium_6 = Natural_Isotope("Li", 6, 6.015122, 7.59, 0.0385003)
Lithium_7 = Natural_Isotope("Li", 7, 7.016004, 92.41, 0.045402)
Beryllium_9 = Natural_Isotope("Be", 9, 9.012182, 100, 0.0100308)
Boron_10 = Natural_Isotope("B", 10, 10.012937, 19.9, 0.499871)
Boron_11 = Natural_Isotope("B", 11, 11.009305, 80.1, 0.00550004)
Carbon_12 = Natural_Isotope("C", 12, 12, 98.93, 0.0035)
Carbon_13 = Natural_Isotope("C", 13, 13.003355, 1.07, 0.0014)
Nitrogen_14 = Natural_Isotope("N", 14, 14.003074, 99.632, 0.0749913)
Nitrogen_15 = Natural_Isotope("N", 15, 15.000109, 0.368, 2.40099e-05)
Oxygen_16 = Natural_Isotope("O", 16, 15.994915, 99.757, 0.000189986)
Oxygen_17 = Natural_Isotope("O", 17, 16.999132, 0.038, 0.00382862)
Oxygen_18 = Natural_Isotope("O", 18, 17.9916, 0.205, 0.00016)
Fluorine_19 = Natural_Isotope("F", 19, 18.998403, 100, 0.00957834)
Neon_20 = Natural_Isotope("Ne", 20, 19.99244, 90.48, 0.040)
Neon_21 = Natural_Isotope("Ne", 21, 20.993847, 0.27, 0.7)
Neon_22 = Natural_Isotope("Ne", 22, 21.991386, 9.25, 0.05)
Sodium_23 = Natural_Isotope("Na", 23, 22.98977, 100, 0.528001)
Magnesium_24 = Natural_Isotope("Mg", 24, 23.985042, 78.99, 0.0502894)
Magnesium_25 = Natural_Isotope("Mg", 25, 24.985837, 10, 0.190374)
Magnesium_26 = Natural_Isotope("Mg", 26, 25.982593, 11.01, 0.03831)
Aluminum_27 = Natural_Isotope("Al", 27, 26.981538, 100, 0.233463)
Silicon_28 = Natural_Isotope("Si", 28, 27.976927, 92.2297, 0.169141)
Silicon_29 = Natural_Isotope("Si", 29, 28.976495, 4.6832, 0.119961)
Silicon_30 = Natural_Isotope("Si", 30, 29.97377, 3.0872, 0.107085)
Phosphorus_31 = Natural_Isotope("P", 31, 30.973762, 100, 0.169361)
Sulfur_32 = Natural_Isotope("S", 32, 31.972071, 94.93, 0.528215)
Sulfur_33 = Natural_Isotope("S", 33, 32.971458, 0.76, 0.350075)
Sulfur_34 = Natural_Isotope("S", 34, 33.967867, 4.29, 0.223618)
Sulfur_36 = Natural_Isotope("S", 36, 35.967081, 0.02, 0.150482)
Chlorine_35 = Natural_Isotope("Cl", 35, 34.968853, 75.78, 43.6122)
Chlorine_37 = Natural_Isotope("Cl", 37, 36.965903, 24.22, 0.43311)
Argon_36 = Natural_Isotope("Ar", 36, 35.967546, 0.3365, 5.04467)
Argon_38 = Natural_Isotope("Ar", 38, 37.962732, 0.0632, 0.80184)
Argon_40 = Natural_Isotope("Ar", 40, 39.962383, 99.6003, 0.660152)
Potassium_39 = Natural_Isotope("K", 39, 38.963707, 93.2581, 2.12742)
Potassium_40 = Natural_Isotope("K", 40, 39.963999, 0.0117, 30.0098)
Potassium_41 = Natural_Isotope("K", 41, 40.961826, 6.7302, 1.46113)
Calcium_40 = Natural_Isotope("Ca", 40, 39.962591, 96.941, 0.407588)
Calcium_42 = Natural_Isotope("Ca", 42, 41.958618, 0.647, 0.683094)
Calcium_43 = Natural_Isotope("Ca", 43, 42.958768, 0.135, 11.6649)
Calcium_44 = Natural_Isotope("Ca", 44, 43.955481, 2.086, 0.888633)
Calcium_46 = Natural_Isotope("Ca", 46, 45.953693, 0.004, 0.740179)
Calcium_48 = Natural_Isotope("Ca", 48, 47.952534, 0.187, 1.09293)
Scandium_45 = Natural_Isotope("Sc", 45, 44.96691, 100, 27.1628)
Titanium_46 = Natural_Isotope("Ti", 46, 45.952629, 8.25, 0.589748)
Titanium_47 = Natural_Isotope("Ti", 47, 46.951764, 7.44, 1.62638)
Titanium_48 = Natural_Isotope("Ti", 48, 47.947947, 73.72, 8.31791)
Titanium_49 = Natural_Isotope("Ti", 49, 48.947871, 5.41, 1.86282)
Titanium_50 = Natural_Isotope("Ti", 50, 49.944792, 5.18, 0.179537)
Vanadium_50 = Natural_Isotope("V", 50, 49.947163, 0.25, 44.6849)
Vanadium_51 = Natural_Isotope("V", 51, 50.943964, 99.75, 4.91912)
Chromium_50 = Natural_Isotope("Cr", 50, 49.94605, 4.345, 15.4049)
Chromium_52 = Natural_Isotope("Cr", 52, 51.940512, 83.789, 0.856093)
Chromium_53 = Natural_Isotope("Cr", 53, 52.940654, 9.501, 18.0927)
Chromium_54 = Natural_Isotope("Cr", 54, 53.938885, 2.365, 0.411198)
Manganese_55 = Natural_Isotope("Mn", 55, 54.93805, 100, 13.2784)
Iron_54 = Natural_Isotope("Fe", 54, 53.939615, 5.845, 2.25193)
Iron_56 = Natural_Isotope("Fe", 56, 55.934942, 91.754, 2.58936)
Iron_57 = Natural_Isotope("Fe", 57, 56.935399, 2.119, 2.42654)
Iron_58 = Natural_Isotope("Fe", 58, 57.93328, 0.282, 1.14965)
Cobalt_59 = Natural_Isotope("Co", 59, 58.9332, 100, 37.1837)
Nickel_58 = Natural_Isotope("Ni", 58, 57.935348, 68.0769, 4.22661)
Nickel_60 = Natural_Isotope("Ni", 60, 59.930791, 26.2231, 2.40101)
Nickel_61 = Natural_Isotope("Ni", 61, 60.93106, 1.1399, 2.5094)
Nickel_62 = Natural_Isotope("Ni", 62, 61.928349, 3.6345, 14.9058)
Nickel_64 = Natural_Isotope("Ni", 64, 63.92797, 0.9256, 1.48038)
Copper_63 = Natural_Isotope("Cu", 63, 62.929601, 69.17, 4.47031)
Copper_65 = Natural_Isotope("Cu", 65, 64.927794, 30.93, 2.14927)
Zinc_64 = Natural_Isotope("Zn", 64, 63.929147, 48.63, 0.787472)
Zinc_66 = Natural_Isotope("Zn", 66, 65.926037, 27.9, 0.617964)
Zinc_67 = Natural_Isotope("Zn", 67, 66.927131, 4.1, 7.47184)
Zinc_68 = Natural_Isotope("Zn", 68, 67.924848, 18.75, 1.0655)
Zinc_70 = Natural_Isotope("Zn", 70, 69.925325, 0.62, 0.0917385)
Gallium_69 = Natural_Isotope("Ga", 69, 68.925581, 60.108, 1.73069)
Gallium_71 = Natural_Isotope("Ga", 71, 70.924705, 39.892, 4.73143)
Germanium_70 = Natural_Isotope("Ge", 70, 69.92425, 20.84, 3.05256)
Germanium_72 = Natural_Isotope("Ge", 72, 71.922076, 27.45, 0.885938)
Germanium_73 = Natural_Isotope("Ge", 73, 72.923459, 7.73, 14.705)
Germanium_74 = Natural_Isotope("Ge", 74, 73.921178, 36.28, 0.519036)
Germanium_76 = Natural_Isotope("Ge", 76, 75.921403, 7.61, 0.154659)
Arsenic_75 = Natural_Isotope("As", 75, 74.921596, 100, 4.50161)
Selenium_74 = Natural_Isotope("Se", 74, 73.922477, 0.89, 51.8151)
Selenium_76 = Natural_Isotope("Se", 76, 75.919214, 9.37, 85.0218)
Selenium_77 = Natural_Isotope("Se", 77, 76.919915, 7.63, 42.0096)
Selenium_78 = Natural_Isotope("Se", 78, 77.91731, 23.77, 0.430126)
Selenium_80 = Natural_Isotope("Se", 80, 79.91652, 49.61, 0.610202)
Selenium_82 = Natural_Isotope("Se", 81, 81.9167, 8.73, 0.0444242)
Bromine_79 = Natural_Isotope("Br", 79, 78.918338, 50.69, 11.0042)
Bromine_81 = Natural_Isotope("Br", 81, 80.916291, 49.31, 2.3651)
Krypton_78 = Natural_Isotope("Kr", 78, 77.920386, 0.35, 6.35568)
Krypton_80 = Natural_Isotope("Kr", 80, 79.916378, 2.28, 11.5046)
Krypton_82 = Natural_Isotope("Kr", 82, 81.913485, 11.58, 19.1672)
Krypton_83 = Natural_Isotope("Kr", 83, 82.914136, 11.49, 198.19)
Krypton_84 = Natural_Isotope("Kr", 84, 83.911507, 57, 0.110022)
Krypton_86 = Natural_Isotope("Kr", 86, 85.91061, 17.3, 0.000878224)
Rubidium_85 = Natural_Isotope("Rb", 85, 84.911789, 72.17, 0.493607)
Rubidium_87 = Natural_Isotope("Rb", 86, 86.909183, 27.83, 0.120037)
Strontium_84 = Natural_Isotope("Sr", 84, 83.913425, 0.56, 0.82219)
Strontium_86 = Natural_Isotope("Sr", 86, 85.909262, 9.86, 1.00556)
Strontium_87 = Natural_Isotope("Sr", 87, 86.908879, 7, 16.0085)
Strontium_88 = Natural_Isotope("Sr", 88, 87.905848, 82.58, 0.00868793)
Yttrium_89 = Natural_Isotope("Y", 89, 88.905848, 100, 1.2787)
Zirconium_90 = Natural_Isotope("Zr", 90, 89.904704, 51.45, 0.00997575)
Zirconium_91 = Natural_Isotope("Zr", 91, 90.905645, 11.22, 1.21603)
Zirconium_92 = Natural_Isotope("Zr", 92, 91.90504, 17.15, 0.229231)
Zirconium_94 = Natural_Isotope("Zr", 94, 93.906316, 17.38, 0.0498845)
Zirconium_96 = Natural_Isotope("Zr", 96, 95.908276, 2.8, 0.0228521)
Niobium_93 = Natural_Isotope("Nb", 93, 92.906378, 100, 1.15554)
Molybdenum_92 = Natural_Isotope("Mo", 92, 91.90681, 14.84, 0.0798857)
Molybdenum_94 = Natural_Isotope("Mo", 94, 93.905088, 9.25, 0.340371)
Molybdenum_95 = Natural_Isotope("Mo", 95, 94.905841, 15.92, 13.3957)
Molybdenum_96 = Natural_Isotope("Mo", 96, 95.904679, 16.68, 0.595576)
Molybdenum_97 = Natural_Isotope("Mo", 97, 96.906021, 9.55, 2.19677)
Molybdenum_98 = Natural_Isotope("Mo", 98, 97.905408, 24.13, 0.130026)
Molybdenum_100 = Natural_Isotope("Mo", 100, 99.907477, 9.63, 0.199087)
Ruthenium_96 = Natural_Isotope("Ru", 96, 95.907598, 5.54, 0.290132)
Ruthenium_98 = Natural_Isotope("Ru", 98, 97.905287, 1.87, 8.00361)
Ruthenium_99 = Natural_Isotope("Ru", 99, 98.905939, 12.76, 7.31152)
Ruthenium_100 = Natural_Isotope("Ru", 100, 99.90422, 12.6, 5.79179)
Ruthenium_101 = Natural_Isotope("Ru", 101, 100.905582, 17.06, 5.22585)
Ruthenium_102 = Natural_Isotope("Ru", 102, 1101.90435, 31.55, 1.27024)
Ruthenium_104 = Natural_Isotope("Ru", 104, 103.90543, 18.62, 0.471636)
Rhodium_103 = Natural_Isotope("Rh", 103, 102.905504, 100, 142.13)
Palladium_102 = Natural_Isotope("Pd", 102, 101.905608, 1.02, 1.82175)
Palladium_104 = Natural_Isotope("Pd", 104, 103.904035, 11.14, 0.648775)
Palladium_105 = Natural_Isotope("Pd", 105, 104.905084, 22.33, 20.8813)
Palladium_106 = Natural_Isotope("Pd", 106, 105.903483, 27.33, 0.30831)
Palladium_108 = Natural_Isotope("Pd", 108, 107.903894, 26.46, 8.48118)
Palladium_110 = Natural_Isotope("Pd", 110, 109.905152, 11.72, 0.229065)
Silver_107 = Natural_Isotope("Ag", 107, 106.905093, 51.839, 37.6085)
Silver_109 = Natural_Isotope("Ag", 109, 108.904756, 48.161, 90.2639)
Cadmium_106 = Natural_Isotope("Cd", 106, 105.906458, 1.25, 0.985925)
Cadmium_108 = Natural_Isotope("Cd", 108, 107.904183, 0.89, 0.905986)
Cadmium_110 = Natural_Isotope("Cd", 110, 109.903006, 12.49, 11.0017)
Cadmium_111 = Natural_Isotope("Cd", 111, 110.904182, 12.8, 6.8683)
Cadmium_112 = Natural_Isotope("Cd", 112, 111.902757, 24.13, 2.19876)
Cadmium_113 = Natural_Isotope("Cd", 113, 112.904401, 12.22, 19964.1)
Cadmium_114 = Natural_Isotope("Cd", 114, 113.903358, 28.73, 0.305462)
Cadmium_116 = Natural_Isotope("Cd", 116, 115.904755, 7.49, 0.0761819)
Indium_113 = Natural_Isotope("In", 113, 112.904061, 4.29, 12.1347)
Indium_115 = Natural_Isotope("In", 115, 114.903878, 95.71, 202.272)
Tin_112 = Natural_Isotope("Sn", 112, 111.904821, 0.97, 0.850333)
Tin_114 = Natural_Isotope("Sn", 114, 113.902782, 0.66, 0.12533)
Tin_115 = Natural_Isotope("Sn", 115, 114.903346, 0.34, 58.0177)
Tin_116 = Natural_Isotope("Sn", 116, 115.901744, 14.54, 0.127698)
Tin_117 = Natural_Isotope("Sn", 117, 116.902954, 7.68, 1.07097)
Tin_118 = Natural_Isotope("Sn", 118, 117.901606, 24.22, 0.219838)
Tin_119 = Natural_Isotope("Sn", 119, 118.903309, 8.59, 2.17455)
Tin_120 = Natural_Isotope("Sn", 120, 119.902197, 32.58, 0.139557)
Tin_122 = Natural_Isotope("Sn", 122, 121.90344, 4.63, 0.146058)
Tin_124 = Natural_Isotope("Sn", 124, 123.905275, 5.79, 0.133765)
Antimony_121 = Natural_Isotope("Sb", 121, 120.903818, 57.21, 5.77312)
Antimony_123 = Natural_Isotope("Sb", 123, 122.904216, 42.79, 3.87523)
Tellurium_120 = Natural_Isotope("Te", 120, 119.904020, 0.09, 2.34103)
Tellurium_122 = Natural_Isotope("Te", 122, 121.903047, 2.55, 3.27307)
Tellurium_123 = Natural_Isotope("Te", 123, 122.904273, 0.89, 418.347)
Tellurium_124 = Natural_Isotope("Te", 124, 123.902819, 4.74, 6.32463)
Tellurium_125 = Natural_Isotope("Te", 125, 124.904425, 7.07, 1.28696)
Tellurium_126 = Natural_Isotope("Te", 126, 125.903306, 18.84, 0.442305)
Tellurium_128 = Natural_Isotope("Te", 128, 127.904461, 31.74, 0.199993)
Tellurium_130 = Natural_Isotope("Te", 130, 129.906223, 34.08, 0.195241)
Iodine_127 = Natural_Isotope("I", 127, 126.904468, 100, 6.14643)
Xenon_124 = Natural_Isotope("Xe", 124, 123.905896, 0.09, 150.2)
Xenon_126 = Natural_Isotope("Xe", 126, 125.903530, 0.09, 3.4874)
Xenon_128 = Natural_Isotope("Xe", 128, 127.903530, 1.92, 5.19249)
Xenon_129 = Natural_Isotope("Xe", 129, 128.904779, 26.44, 21.0066)
Xenon_130 = Natural_Isotope("Xe", 130, 129.903508, 4.08, 4.77859)
Xenon_131 = Natural_Isotope("Xe", 131, 130.905082, 21.18, 90.0327)
Xenon_132 = Natural_Isotope("Xe", 132, 131.904154, 26.89, 0.450652)
Xenon_134 = Natural_Isotope("Xe", 134, 133.905395, 10.44, 0.26489)
Xenon_136 = Natural_Isotope("Xe", 136, 135.907220, 8.87, 0.260738)
Cesium_133 = Natural_Isotope("Cs", 133, 132.905447, 100, 29.0552)
Barium_130 = Natural_Isotope("Ba", 130, 129.906310, 0.106, 8.68002)
Barium_132 = Natural_Isotope("Ba", 132, 131.905056, 0.101, 6.53133)
Barium_134 = Natural_Isotope("Ba", 134, 133.904503, 2.417, 1.50433)
Barium_135 = Natural_Isotope("Ba", 135, 134.905683, 6.592, 5.87216)
Barium_136 = Natural_Isotope("Ba", 136, 135.904570, 7.854, 0.679633)
Barium_137 = Natural_Isotope("Ba", 137, 136.905821, 11.232, 3.59734)
Barium_138 = Natural_Isotope("Ba", 138, 137.905241, 71.698, 0.403537)
Lanthanum_138 = Natural_Isotope("La", 138, 137.907107, 0.09, 57.1047)
Lanthanum_139 = Natural_Isotope("La", 139, 138.907107, 99.91, 9.0416)
Cerium_136 = Natural_Isotope("Ce", 136, 135.907144, 0.185, 7.45753)
Cerium_138 = Natural_Isotope("Ce", 138, 137.905986, 0.251, 1.03713)
Cerium_140 = Natural_Isotope("Ce", 140, 139.905434, 88.45, 0.577524)
Cerium_142 = Natural_Isotope("Ce", 142, 141.90924, 11.114, 0.96504)
Praseodymium_141 = Natural_Isotope("Pr", 141, 140.9076448, 100, 11.5092)
Neodymium_142 = Natural_Isotope("Nd", 142, 141.907719, 27.2, 18.702)
Neodymium_143 = Natural_Isotope("Nd", 143, 142.90981, 12.2, 325.207)
Neodymium_144 = Natural_Isotope("Nd", 144, 143.910083, 23.8, 3.59476)
Neodymium_145 = Natural_Isotope("Nd", 145, 144.912569, 8.3, 42.0042)
Neodymium_146 = Natural_Isotope("Nd", 146, 145.913112, 17.2, 1.48972)
Neodymium_148 = Natural_Isotope("Nd", 148, 147.916889, 5.7, 2.58455)
Neodymium_150 = Natural_Isotope("Nd", 150, 149.920887, 5.6, 1.04087)
Samarium_144 = Natural_Isotope("Sm", 144, 143.911995, 3.07, 1.63074)
Samarium_147 = Natural_Isotope("Sm", 147, 146.914893, 14.99, 57.0005)
Samarium_148 = Natural_Isotope("Sm", 148, 147.914818, 11.24, 2.40081)
Samarium_149 = Natural_Isotope("Sm", 149, 148.91718, 13.82, 40513.5)
Samarium_150 = Natural_Isotope("Sm", 150, 149.917271, 7.38, 100.028)
Samarium_152 = Natural_Isotope("Sm", 152, 151.919728, 26.75, 206.002)
Samarium_154 = Natural_Isotope("Sm", 154, 153.922205, 22.75, 8.32501)
Europium_151 = Natural_Isotope("Eu", 151, 150.919846, 47.81, 9185.34)
Europium_153 = Natural_Isotope("Eu", 153, 152.921226, 52.19, 358.045)
Gadolinium_152 = Natural_Isotope("Gd", 152, 151.919788, 0.2, 735.135)
Gadolinium_154 = Natural_Isotope("Gd", 154, 1553.920862, 2.18, 85.2086)
Gadolinium_155 = Natural_Isotope("Gd", 155, 154.922619, 14.8, 60740.1)
Gadolinium_156 = Natural_Isotope("Gd", 156, 155.92212, 20.47, 1.7951)
Gadolinium_157 = Natural_Isotope("Gd", 157, 156.923957, 15.65, 252928)
Gadolinium_158 = Natural_Isotope("Gd", 158, 157.924101, 24.84, 2.20303)
Gadolinium_160 = Natural_Isotope("Gd", 160, 159.927051, 21.86, 1.41027)
Terbium_159 = Natural_Isotope("Tb", 159, 158.925343, 100, 23.3595)
Dysprosium_156 = Natural_Isotope("Dy", 156, 155.924278, 0.06, 33.0649)
Dysprosium_158 = Natural_Isotope("Dy", 158, 157.924405, 0.1, 43.0828)
Dysprosium_160 = Natural_Isotope("Dy", 160, 159.925194, 2.34, 55.9966)
Dysprosium_161 = Natural_Isotope("Dy", 161, 160.92693, 18.91, 600.248)
Dysprosium_162 = Natural_Isotope("Dy", 162, 161.926795, 25.51, 193.986)
Dysprosium_163 = Natural_Isotope("Dy", 163, 162.928728, 24.9, 123.433)
Dysprosium_164 = Natural_Isotope("Dy", 164, 163.929171, 28.18, 2653.58)
Holmium_165 = Natural_Isotope("Ho", 165, 164.930319, 100, 64.6959)
Erbium_162 = Natural_Isotope("Er", 162, 161.928775, 0.14, 18.9178)
Erbium_164 = Natural_Isotope("Er", 164, 163.929197, 1.61, 12.9572)
Erbium_166 = Natural_Isotope("Er", 166, 165.93029, 33.61, 16.8769)
Erbium_167 = Natural_Isotope("Er", 167, 166.932045, 22.93, 649.812)
Erbium_168 = Natural_Isotope("Er", 168, 167.932368, 26.78, 2.74199)
Erbium_170 = Natural_Isotope("Er", 170, 160.93546, 14.94, 8.8531)
Thulium_169 = Natural_Isotope("Tm", 169, 168.934211, 100, 105.049)
Ytterbium_168 = Natural_Isotope("Yb", 168, 167.933894, 0.13, 2308.65)
Ytterbium_170 = Natural_Isotope("Yb", 170, 169.934759, 3.04, 10.4239)
Ytterbium_171 = Natural_Isotope("Yb", 171, 170.936322, 14.28, 55.1482)
Ytterbium_172 = Natural_Isotope("Yb", 172, 171.936378, 21.83, 1.13789)
Ytterbium_173 = Natural_Isotope("Yb", 173, 172.938207, 16.13, 16.0429)
Ytterbium_174 = Natural_Isotope("Yb", 174, 173.938858, 31.83, 66.2165)
Ytterbium_176 = Natural_Isotope("Yb", 176, 175.942568, 12.76, 2.8382)
Lutetium_175 = Natural_Isotope("Lu", 175, 174.940768, 97.41, 23.0819)
Lutetium_176 = Natural_Isotope("Lu", 176, 175.942682, 2.59, 2096.98)
Hafnium_174 = Natural_Isotope("Hf", 174, 173.94004, 0.16, 549.546)
Hafnium_176 = Natural_Isotope("Hf", 176, 175.941402, 5.26, 21.3847)
Hafnium_177 = Natural_Isotope("Hf", 177, 176.94322, 18.6, 373.667)
Hafnium_178 = Natural_Isotope("Hf", 178, 177.943698, 27.28, 83.9482)
Hafnium_179 = Natural_Isotope("Hf", 179, 178.945815, 13.62, 42.7982)
Hafnium_180 = Natural_Isotope("Hf", 180, 179.946549, 35.08, 13.0744)
Tantalum_180 = Natural_Isotope("Ta", 180, 179.947466, 0.012, 791.213)
Tantalum_181 = Natural_Isotope("Ta", 181, 180.947996, 99.988, 21.1306)
Tungsten_180 = Natural_Isotope("W", 180, 179.946706, 0.12, 29.6565)
Tungsten_182 = Natural_Isotope("W", 182, 181.948206, 26.5, 20.7155)
Tungsten_183 = Natural_Isotope("W", 183, 182.950224, 14.31, 10.1168)
Tungsten_184 = Natural_Isotope("W", 184, 183.950933, 30.64, 1.50204)
Tungsten_186 = Natural_Isotope("W", 186, 185.954362, 28.43, 38.0949)
Rhenium_185 = Natural_Isotope("Re", 185, 184.952956, 37.4, 112.176)
Rhenium_187 = Natural_Isotope("Re", 187, 186.955751, 62.6, 76.7062)
Osmium_184 = Natural_Isotope("Os", 184, 183.952491, 0.02, 3081.89)
Osmium_186 = Natural_Isotope("Os", 186, 185.953838, 1.59, 80.35977)
Osmium_187 = Natural_Isotope("Os", 187, 186.955748, 1.96, 320.331)
Osmium_188 = Natural_Isotope("Os", 188, 187.955836, 1.96, 5.22819)
Osmium_189 = Natural_Isotope("Os", 189, 188.958145, 13.24, 25.0801)
Osmium_190 = Natural_Isotope("Os", 190, 189.958445, 26.26, 13.0864)
Osmium_192 = Natural_Isotope("Os", 192, 191.961479, 40.78, 2.74746)
Iridium_191 = Natural_Isotope("Ir", 191, 190.960591, 37.3, 954.468)
Iridium_193 = Natural_Isotope("Ir", 193, 192.962924, 62.7, 111.173)
Platinum_190 = Natural_Isotope("Pt", 190, 189.95993, 0.014, 153.122)
Platinum_192 = Natural_Isotope("Pt", 192, 191.961035, 0.782, 10.6592)
Platinum_194 = Natural_Isotope("Pt", 194, 193.962664, 32.967, 1.37928)
Platinum_195 = Natural_Isotope("Pt", 195, 194.964774, 33.832, 27.5463)
Platinum_196 = Natural_Isotope("Pt", 196, 195.964935, 25.242, 0.6488625)
Platinum_198 = Natural_Isotope("Pt", 198, 197.967876, 7.163, 3.51825)
Gold_197 = Natural_Isotope("Au", 197, 196.966552, 100, 99.10925)
Mercury_196 = Natural_Isotope("Hg", 196, 195.965815, 0.15, 3078.91)
Mercury_198 = Natural_Isotope("Hg", 198, 197.966752, 9.97, 1.98586)
Mercury_199 = Natural_Isotope("Hg", 199, 198.968262, 16.87, 2150.18)
Mercury_200 = Natural_Isotope("Hg", 200, 199.968309, 23.1, 1.44314)
Mercury_201 = Natural_Isotope("Hg", 201, 200.970285, 13.18, 4.90396)
Mercury_202 = Natural_Isotope("Hg", 202, 201.970626, 29.86, 4.95514)
Mercury_204 = Natural_Isotope("Hg", 204, 203.973476, 6.87, 0.431558)
Thallium_203 = Natural_Isotope("Tl", 203, 202.972329, 29.524, 11.411)
Thallium_205 = Natural_Isotope("Tl", 205, 204.974412, 70.476, 0.130514)
Lead_204 = Natural_Isotope("Pb", 204, 203.973029, 1.4, 0.660895)
Lead_206 = Natural_Isotope("Pb", 206, 205.974449, 24.1, 0.0297921)
Lead_207 = Natural_Isotope("Pb", 207, 206.975881, 22.1, 0.712178)
Lead_208 = Natural_Isotope("Pb", 208, 207.976636, 52.4, 0.000232076)
Bismuth_209 = Natural_Isotope("Bi", 209, 208.980383, 100, 0.0338121)
Thorium_232 = Natural_Isotope("Th", 232, 232.0385879, 100, 7.33806)
Proactinium_231 = Natural_Isotope("Pa", 231, 231.035879, 100, 200.689)
Uranium_234 = Natural_Isotope("U", 234, 234.040946, 0.0055, 100.908)
Uranium_235 = Natural_Isotope("U", 235, 235.043923, 0.72, 98.6866)
Uranium_238 = Natural_Isotope("U", 238, 238.050783, 99.2745, 2.68346)

natural_isotope_list = [Hydrogen_1, Hydrogen_2, Helium_3, Helium_4, Lithium_6,
                        Lithium_7, Beryllium_9, Boron_10, Boron_11, Carbon_12,
                        Carbon_13, Nitrogen_14, Nitrogen_15, Oxygen_16,
                        Oxygen_17, Oxygen_18, Fluorine_19, Neon_20, Neon_21,
                        Neon_22, Sodium_23, Magnesium_24, Magnesium_25,
                        Magnesium_26, Aluminum_27, Silicon_28, Silicon_29,
                        Silicon_30, Phosphorus_31, Sulfur_32, Sulfur_33,
                        Sulfur_34, Sulfur_36, Chlorine_35, Chlorine_37,
                        Argon_36, Argon_38, Argon_40, Potassium_39,
                        Potassium_40, Potassium_41, Calcium_40, Calcium_42,
                        Calcium_43, Calcium_44, Calcium_46, Calcium_48,
                        Scandium_45, Titanium_46, Titanium_47, Titanium_48,
                        Titanium_49, Titanium_50, Vanadium_50, Vanadium_51,
                        Chromium_50, Chromium_52, Chromium_53, Chromium_54,
                        Manganese_55, Iron_54, Iron_56, Iron_57, Iron_58,
                        Cobalt_59, Nickel_58, Nickel_60, Nickel_61, Nickel_62,
                        Nickel_64, Copper_63, Copper_65, Zinc_64, Zinc_66,
                        Zinc_67, Zinc_68, Zinc_70, Gallium_69, Gallium_71,
                        Germanium_70, Germanium_72, Germanium_73, Germanium_74,
                        Germanium_76, Arsenic_75, Selenium_74, Selenium_76,
                        Selenium_77, Selenium_78, Selenium_80, Selenium_82,
                        Bromine_79, Bromine_81, Krypton_78, Krypton_80,
                        Krypton_82, Krypton_83, Krypton_84, Krypton_86,
                        Rubidium_85, Rubidium_87, Strontium_84, Strontium_86,
                        Strontium_87, Strontium_88, Yttrium_89, Zirconium_90,
                        Zirconium_91, Zirconium_92, Zirconium_94, Zirconium_96,
                        Niobium_93, Molybdenum_92, Molybdenum_94,
                        Molybdenum_95, Molybdenum_96, Molybdenum_97,
                        Molybdenum_98, Molybdenum_100, Ruthenium_96,
                        Ruthenium_98, Ruthenium_99, Ruthenium_100,
                        Ruthenium_101, Ruthenium_102, Ruthenium_104,
                        Rhodium_103, Palladium_102, Palladium_104,
                        Palladium_105, Palladium_106, Palladium_108,
                        Palladium_110, Silver_107, Silver_109, Cadmium_106,
                        Cadmium_108, Cadmium_110, Cadmium_111, Cadmium_112,
                        Cadmium_113, Cadmium_114, Cadmium_116, Indium_113,
                        Indium_115, Tin_112, Tin_114, Tin_115, Tin_116,
                        Tin_117, Tin_118, Tin_119, Tin_120, Tin_122, Tin_124,
                        Antimony_121, Antimony_123, Tellurium_120,
                        Tellurium_122, Tellurium_123, Tellurium_124,
                        Tellurium_125, Tellurium_126, Tellurium_128,
                        Tellurium_130, Iodine_127, Xenon_124, Xenon_126,
                        Xenon_128, Xenon_129, Xenon_130, Xenon_131, Xenon_132,
                        Xenon_134, Xenon_136, Cesium_133, Barium_130,
                        Barium_132, Barium_134, Barium_135, Barium_136,
                        Barium_137, Barium_138, Lanthanum_138, Lanthanum_139,
                        Cerium_136, Cerium_138, Cerium_140, Cerium_142,
                        Praseodymium_141, Neodymium_142, Neodymium_143,
                        Neodymium_144, Neodymium_145, Neodymium_146,
                        Neodymium_148, Neodymium_150, Samarium_144,
                        Samarium_147, Samarium_148, Samarium_149, Samarium_150,
                        Samarium_152, Samarium_154, Europium_151, Europium_153,
                        Gadolinium_152, Gadolinium_154, Gadolinium_155,
                        Gadolinium_156, Gadolinium_157, Gadolinium_158,
                        Gadolinium_160, Terbium_159, Dysprosium_156,
                        Dysprosium_158, Dysprosium_160, Dysprosium_161,
                        Dysprosium_162, Dysprosium_163, Dysprosium_164,
                        Holmium_165, Erbium_162, Erbium_164, Erbium_166,
                        Erbium_167, Erbium_168, Erbium_170, Thulium_169,
                        Ytterbium_168, Ytterbium_170, Ytterbium_171,
                        Ytterbium_172, Ytterbium_173, Ytterbium_174,
                        Ytterbium_176, Lutetium_175, Lutetium_176,
                        Hafnium_174, Hafnium_176, Hafnium_177, Hafnium_178,
                        Hafnium_179, Hafnium_180, Tantalum_180, Tantalum_181,
                        Tungsten_180, Tungsten_182, Tungsten_183, Tungsten_184,
                        Tungsten_186, Rhenium_185, Rhenium_187, Osmium_184,
                        Osmium_186, Osmium_187, Osmium_188, Osmium_189,
                        Osmium_190, Osmium_192, Iridium_191,
                        Iridium_193, Platinum_190, Platinum_192, Platinum_194,
                        Platinum_195, Platinum_196, Platinum_198, Gold_197,
                        Mercury_196, Mercury_198, Mercury_199, Mercury_200,
                        Mercury_201, Mercury_202, Mercury_204, Thallium_203,
                        Thallium_205, Lead_204, Lead_206, Lead_207, Lead_208,
                        Bismuth_209, Thorium_232, Proactinium_231, Uranium_234,
                        Uranium_235, Uranium_238]
