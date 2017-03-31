from ROI_Maker import (ROI_Maker, peak_measurement, emission_rate,
                      background_subtract, absolute_efficiency, isotope_activity)
import SPEFile

class ReferenceBase(object):
    """
    Generates a reference object that contains a reference mass and
    concentrations. Mass is in kg and concentrations are in percent for
    K-40 and ppm for the rest. Conversions are currently unknown in their
    origin and derivation.
    """


    def __init__(self, mass, ref_concentration, ref_concentration_error,
                 conversion, spectrum=None):
        self.mass = mass
        self.ref_concentration = ref_concentration
        self.ref_concentration_error = ref_concentration_error
        self.conversion = conversion
        self.spectrum = spectrum


    def get_spec_countrates(self, isotope, background):
        reference = self.spectrum
        ref_spec_count_rate = []
        ref_spec_ct_rate_error = []

        for energy in isotope.list_sig_g_e:
            reference_peak = peak_measurement(reference, energy)
            background_peak = peak_measurement(background, energy)
            reference_area = background_subtract(reference_peak,
                                                 background_peak,
                                                 reference.livetime,
                                                 background.livetime)
            ref_spec_count_rate.append(reference_area[0]/(reference.livetime*self.mass))
            ref_spec_ct_rate_error.append(reference_area[1]/(reference.livetime*self.mass))

        return ref_spec_count_rate, ref_spec_ct_rate_error


    def get_spec_activity(self, isotope, background):
        spec_countrates, spec_countrates_error = self.get_spec_countrates(isotope, background=background)
        spec_emissions = []
        spec_emissions_error = []
        for i, energy in enumerate(isotope.list_sig_g_e):
            eff = absolute_efficiency([energy])[0]
            spec_em = spec_countrates[i] / eff
            spec_em_err = spec_countrates_error[i] / eff
            spec_emissions.append(spec_em)
            spec_emissions_error.append(spec_em_err)
        act = isotope_activity(isotope, spec_emissions, spec_emissions_error)
        return act


class PetriReference(ReferenceBase):
    """
    Uses the Petri dish sample data as the reference.
    """

    def __init__(self, ref_specific_count_rate, ref_spec_ct_rate_error,
                 **kwargs):
        self.ref_spec_ct_rate = ref_specific_count_rate
        self.ref_spec_ct_rate_error = ref_spec_ct_rate_error
        ReferenceBase.__init__(self, **kwargs)

    def get_spec_countrates(self, isotope, **kwargs):
        isotope_name = isotope.symbol + str(isotope.mass_number)
        return (self.ref_spec_ct_rate[isotope_name],
                self.ref_spec_ct_rate_error[isotope_name])


# Create a list of samples that uses an alternate reference.
alt_ref_samples = ['UCB027']
# Define the mass for the Petri soil reference sample.
dirt_petri_mass = 1.18360
petri_specific_count_rate = {'K40': [2.15E-01],
                             'Bi214': [8.28E-03, 8.56E-03, 4.11E-02],
                             'Tl208': [9.35E-03, 2.17E-02]}

petri_spec_ct_rate_error = {'K40': [1.55E-03],
                             'Bi214': [3.54E-04, 4.69E-04, 8.05E-04],
                             'Tl208': [3.96E-04, 6.59E-04]}

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


S5F_spectrum = SPEFile.SPEFile("UCB018_Soil_Sample010_2.Spe")
S5F_spectrum.read()

S5F_reference = ReferenceBase(dirt_S5F_mass, dirt_concentrations,
                           dirt_concentrations_uncertainty, dirt_conversions,
                           S5F_spectrum)
petri_reference = PetriReference(
    mass=dirt_petri_mass, 
    ref_concentration=dirt_concentrations,
    ref_concentration_error=dirt_concentrations_uncertainty, 
    conversion=dirt_conversions,
    ref_specific_count_rate=petri_specific_count_rate,
    ref_spec_ct_rate_error=petri_spec_ct_rate_error)