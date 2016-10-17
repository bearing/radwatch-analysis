

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

dirt_mass = 2.380
dirt_k_40 = 2.57
dirt_bi_214 = 1.97
dirt_pb_214 = 1.97
dirt_th_234 = 2.26
dirt_tl_208 = 5.08
dirt_ac_228 = 5.43
dirt_pb_212 = 5.08

dirt_k_40_unc = 0.01
dirt_bi_214_unc = 0.02
dirt_pb_214_unc = 0.02
dirt_th_234_unc = 0.07
dirt_tl_208_unc = 0.05
dirt_ac_228_unc = 0.07
dirt_pb_212_unc = 0.05
dirt_concentrations = [dirt_k_40, dirt_bi_214, dirt_pb_214, dirt_th_234,
                       dirt_tl_208, dirt_ac_228, dirt_pb_212]
dirt_concentrations_uncertainty = [dirt_k_40_unc, dirt_bi_214_unc,
                                   dirt_pb_214_unc, dirt_th_234_unc,
                                   dirt_tl_208_unc, dirt_ac_228_unc,
                                   dirt_pb_212_unc]
dirt_conversions = [309.6, 12.3, 4.07]
soil_reference = Reference(dirt_mass, dirt_concentrations,
                           dirt_concentrations_uncertainty, dirt_conversions)
