def isotope_verifier(isotope):
    """
    Takes in a list of isotopes and checks to see whether or not the isotope is 
    naturally occuring or not. If the isotope is naturally occuring, then the
    module will display the isotope along with its mass number and natural 
    abundance.
    """
    isotope = isotope.symbol + str(isotope.mass_number)
    flag = False
    
    for i in range(len(natural_isotopes_list)):
        var = natural_isotopes_list[i].symbol + str(natural_isotopes_list[i].mass_number)        
        if isotope == var:
            isotope_info = [natural_isotopes_list[i]]
            flag = True
            break
        
    if flag == False:
        isotope_info = ['Isotope is not naturally occuring.']
    
    return(isotope_info)