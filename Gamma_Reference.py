

class Reference(object):
    """
    Generates a reference object that contains a reference mass and
    concentrations. Mass is in kg and concentrations are in percent for
    K-40 and ppm for the rest. Conversions are currently unknown in their
    origin and derivation.
    """
    def __init__(self, mass, ref_concentration, ref_concentration_error,
                 conversion):
        self.mass = mass
        self.ref_concentration = ref_concentration
        self.ref_concentration_error = ref_concentration_error
        self.conversion = conversion

Dirt_Mass = 2.380
Dirt_K_40 = 2.57
Dirt_Bi_214 = 1.97
Dirt_Pb_214 = 1.97
Dirt_Th_234 = 2.26
Dirt_Tl_208 = 5.08
Dirt_Ac_228 = 5.43
Dirt_Pb_212 = 5.08

Dirt_K_40_Unc = 0.01
Dirt_Bi_214_Unc = 0.02
Dirt_Pb_214_Unc = 0.02
Dirt_Th_234_Unc = 0.07
Dirt_Tl_208_Unc = 0.05
Dirt_Ac_228_Unc = 0.07
Dirt_Pb_212_Unc = 0.05
Dirt_Concentrations = [Dirt_K_40, Dirt_Bi_214, Dirt_Pb_214, Dirt_Th_234,
                       Dirt_Tl_208, Dirt_Ac_228, Dirt_Pb_212]
Dirt_Concentrations_Uncertainty = [Dirt_K_40_Unc, Dirt_Bi_214_Unc,
                                   Dirt_Pb_214_Unc, Dirt_Th_234_Unc,
                                   Dirt_Tl_208_Unc, Dirt_Ac_228_Unc,
                                   Dirt_Pb_212_Unc]
Dirt_Conversions = [309.6, 12.3, 4.07]
Soil_Reference = Reference(Dirt_Mass, Dirt_Concentrations,
                           Dirt_Concentrations_Uncertainty, Dirt_Conversions)
