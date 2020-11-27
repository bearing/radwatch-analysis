from naa_Isotopic_Abundance import natural_isotope_list

def isotope_verifier(nndc_info):

    nndc_info_verified_isotope = []
    nndc_info_verified_energy = []
    nndc_info_verified_br = []

    for i in range(len(nndc_info)):
        element = nndc_info[i]['Element']
        atomic_number = nndc_info[i]['A']
        energy_emitted_list = []
        br_list = []
        isotope_list = []

        for j in range(len(element)):
            isotope = element[j] + str(atomic_number[j])
            parent_isotope = element[j] + str(atomic_number[j]-1)
            energy_emitted = nndc_info[i]['Radiation Energy (keV)'][j]
            br = nndc_info[i]['Radiation Intensity (%)'][j]

            for k in range(len(natural_isotope_list)):
                var = natural_isotope_list[k].symbol + str(natural_isotope_list[k].mass_number)

                if parent_isotope == var:
                    isotope_list.append(isotope)
                    energy_emitted_list.append(energy_emitted)
                    br_list.append(br)
                    break

        nndc_info_verified_isotope.append(isotope_list)
        nndc_info_verified_energy.append(energy_emitted_list)
        nndc_info_verified_br.append(br_list)


    return nndc_info_verified_isotope, nndc_info_verified_energy, nndc_info_verified_br