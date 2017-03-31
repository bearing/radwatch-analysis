class ReferenceBase(object):
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

class PetriReference(ReferenceBase):
    """
    Uses the Petri dish sample data as the reference.
    """
    def spec_count_rate(self, mass, ref_concentration, ref_concentration_error,
                 conversion, ref_specific_count_rate):
        self.ref_spec_ct_rate = ref_specific_count_rate

# Create a list of samples that uses an alternate reference.
alt_ref_samples = ['UCB027']
# Define the mass for the Petri soil reference sample.
dirt_petri_mass = 1.18360
petri_specific_count_rate = [3.11E-04, 2.15E-01, 9.35E-03, 2.17E-02, 1.05E-02,
                             1.75E-02, 1.56E-02, 7.27E-02, 8.28E-03, 8.56E-03,
                             4.11E-02, 5.25E-02, 3.10E-02, 1.07E-02, 1.50E-02]

# Define the mass for the S5F soil reference sample.
dirt_S5F_mass = 1.19300
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
soil_reference = ReferenceBase(dirt_S5F_mass, dirt_concentrations,
                           dirt_concentrations_uncertainty, dirt_conversions)
petri_reference = PetriReference(dirt_petri_mass, dirt_concentrations,
                           dirt_concentrations_uncertainty, dirt_conversions,
                           petri_specific_activity)
