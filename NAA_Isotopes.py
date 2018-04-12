import numpy as np


class NAA_source(object):
    sources = []
    def __init__(self, Symbol, A, lam, energies):
        self.Symbol = Symbol
        self.A = A
        self.lam = lam
        self.energies = energies
        NAA_source.sources.append(self)

    def __repr__(self):
        return '{0}_{1}'.format(self.Symbol, self.A + 1)


Na_24_energies = {'energy': [1368.626, 2754.007],
                    'branching_ratio':[1, 0.99855]}

Na_24 = NAA_source('Na', 23, 1.284e-5, Na_24_energies)

K_40_energies = {'energy': [1460.82], 'branching_ratio':[0.1066]}

K_40 = NAA_source ('K', 39, 1.761e-17, K_40_energies)

K_42_energies = {'energy': [1524.7],
                    'branching_ratio': [0.18]}

K_42 = NAA_source('K', 41, 1.56e-5, K_42_energies)

Sc_46_energies = {'energy': [889.277, 1120.545],
                    'branching_ratio': [0.99984, 0.99987]}

Sc_46  = NAA_source('Sc', 45, 2.4e-6, Sc_46_energies)

Ca_47_energies = {'energy':[489.23, 807.86, 1297.09],
                    'branching_ratio':[0.062, 0.062, 0.71]}

Ca_47 = NAA_source('Ca', 46, 1.769e-6, Ca_47_energies)

Cr_51_energies = {'energy': [320.1],
                    'branching_ratio': [0.1]}
Cr_51 = NAA_source('Cr', 50, 2.9e-7, Cr_51_energies)

Mn_56_energies = {'energy':[846.771, 1810.772, 2113.123],
                    'branching_ratio':[0.989, 0.272, 0.143]}
Mn_56 = NAA_source('Mn', 55, 7.467e-5, Mn_56_energies)

Fe_59_energies = {'energy': [1099.43, 1291.79],
                    'branching_ratio': [0.565, 0.432]}

Fe_59 = NAA_source('Fe', 58, 1.8e-7, Fe_59_energies)

Co_60_energies = {'energy': [1173.43, 1332.71],
                    'branching_ratio': [0.999735, 0.999856]}

Co_60 = NAA_source('Co', 59, 4.17e-9, Co_60_energies)

Cu_64_energies = {'energy': [1345.84], 'branching_ratio': [0.00473]}
Cu_64 = NAA_source('Cu', 63, 1.516e-5, Cu_64_energies)

Zn_65_energies = {'energy': [1115.86],
                'branching_ratio': [0.506]}

Zn_65 = NAA_source('Zn', 64, 3.28e-8, Zn_65_energies)

Ga_72_energies = {'energy': [834.01, 629.95, 600.94],
                    'branching_ratio': [0.96, 0.248, 0.0554]}
Ga_72 = NAA_source('Ga', 71, 1.366e-5, Ga_72_energies)

Se_75_energies = {'energy': [121.1155, 136, 264.6576, 279.54, 400.6576],
                    'branching_ratio': [0.172, 0.583, 0.589, 0.2499, 0.1147]}

Se_75 = NAA_source('Se', 74, 6.698e-8, Se_75_energies)

As_76_energies = {'energy': [559.24, 657.25],
                    'branching_ratio': [0.45, 0.052]}

As_76 = NAA_source('As', 75, 7.44e-6, As_76_energies)

Kr_81_energies = {'energy': [275.988], 'branching_ratio': [0.3]}

Kr_81 = NAA_source('Kr', 80, 9.59806e-14, Kr_81_energies)

Br_82_energies = {'energy': [559.49, 619.67, 776.45],
                    'branching_ratio': [0.45, 0.434, 0.835]}

Br_82 = NAA_source('Br', 81, 5.45e-6, Br_82_energies)

Sr_85_energies = {'energy': [514.0067], 'branching_ratio': [0.96]}

Sr_85 = NAA_source('Sr', 84, 1.2373e-7, Sr_85_energies)

Rb_86_energies = {'energy': [1076.96],
                    'branching_ratio': [0.09]}

Rb_86 = NAA_source('Rb', 85, 4.31e-7, Rb_86_energies)

Zr_95_energies = {'energy': [724.2, 759.73], 'branching_ratio': [0.4417, 0.54]}

Zr_95 = NAA_source('Zr', 95, 1.253e-7, Zr_95_energies)

Zr_97_energies = {'energy': [743.36], 'branching_ratio': [.93]}

Zr_97 = NAA_source('Zr', 96, 1.139e-5, Zr_97_energies)

Sb_122_energies = {'energy': [564.12, 692.794],
                    'branching_ratio': [0.71, 0.0385]}

Sb_122 = NAA_source('Sb', 121, 2.945e-6, Sb_122_energies)

Sb_124_energies = {'energy': [602.72, 1690.98],
                    'branching_ratio': [0.9826, 0.4779]}

Sb_124 = NAA_source('Sb', 123, 1.33e-7, Sb_124_energies)

Ba_131_energies = {'energy': [123.81, 216.078, 496.47],
                    'branching_ratio': [0.2897, 0.1966, 0.47]}

Ba_131 = NAA_source('Ba', 130, 6.98e-7, Ba_131_energies)

Cs_134_energies = {'energy': [569.48, 604.721, 796.02],
                    'branching_ratio': [0.1538, 0.9762, 0.8553]}

Cs_134 = NAA_source('Cs', 133, 1.06e-8, Cs_134_energies)

Cs_137_energies= {'energy':[661.657], 'branching_ratio': [0.851]}

Cs_137 = NAA_source('Cs', 136, 7.307e-10, Cs_137_energies)

Cs_138_energies = {'energy': [1435.795], 'branching_ratio': [.763]}

Cs_138 = NAA_source('Cs', 137, .000347, Cs_138_energies)

La_140_energies = {'energy': [328.86, 487.16, 751.81, 815.96, 925.4, 1596.43,
                    2521.64],
                    'branching_ratio': [0.203, 0.455, 0.0433, 0.2328, 0.069,
                    0.954, 0.0346]}

La_140 = NAA_source('La', 139, 5.45e-6, La_140_energies)

Ce_141_energies = {'energy': [145.44],
                    'branching_ratio': [0.482]}

Ce_141 = NAA_source('Ce', 140, 2.48e-7, Ce_141_energies)

Eu_152_energies = {'energy': [121.78, 244.7, 344.35, 778.9, 964.1, 1085.9,
                                1112.1, 1408],
                   'branching_ratio': [0.2858, 0.0758, 0.265, 0.12942,
                                        0.14605, 0.10207, 0.13644, 0.21005]}

Eu_152 = NAA_source('Eu', 151, 1.62e-9, Eu_152_energies)

Eu_154_energies = {'energy': [723,81, 1274.65],
                    'branching_ratio': [0.2022, 0.3519]}

Eu_154 = NAA_source('Eu', 153, 2.45e-9, Eu_154_energies)

Dy_165_energies = {'energy': [361.68], 'branching_ratio': [0.0084]}
Dy_165 = NAA_source('Dy', 164, 8.248e-5, Dy_165_energies)

Hf_181_energies = {'energy': [482.182, 133.024, 345.916],
                    'branching_ratio': [.805, .433, .1512]}
Hf_181 = NAA_source('Hf', 180, 1.893e-7, Hf_181_energies)

Au_198_energies = {'energy': [411.803], 'branching_ratio': [0.96]}

Au_198 = NAA_source('Au', 197, 2.9766e-6, Au_198_energies)

Hg_203_energies = {'energy': [279.197], 'branching_ratio': [0.81]}

Hg_203 = NAA_source('Hg', 202, 1.721e-7, Hg_203_energies)
