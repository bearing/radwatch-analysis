# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 11:45:04 2016

@author: Mustapha Saad
"""

from __future__ import print_function
import bs4
import urllib
import math



"""
gamma_search takes in a peak energy and goes to the webpage at 
http://nucleardata.nuclear.lu.se/toi/ to input the peak energy. The program 
then searches for the radionuclides that emit gamma energies within 1 keV for 
gamma energies below 2000 keV and within 4 keV for gamma energies equal to and 
above 2000 keV. It then outputs a list of urls for radionuclides that emit 
within the gamma energy range and that have an intensity of at least 1% as well
as having a half life of at least 1 hour. These urls are the input for the 
gamma-extract function.
"""



def gamma_search(peak_energy):

    """
    Extracting all information from the webpage into a BeautifulSoup object.
    """

    if peak_energy >= 2000:    
        plus_four = peak_energy + 4
        minus_four = peak_energy - 4    
        url = 'http://nucleardata.nuclear.lu.se/toi/Gamma.asp?sql=&Min=' \
        + str(minus_four) + '&Max=' + str(plus_four) \
        + '&HlifeMin=3600&tMinStr=1+h'
    else:
        plus_one = peak_energy + 1
        minus_one = peak_energy - 1    
        url = 'http://nucleardata.nuclear.lu.se/toi/Gamma.asp?sql=&Min=' \
        + str(minus_one) + '&Max=' + str(plus_one) \
        + '&HlifeMin=3600&tMinStr=1+h'
    
   
    html = urllib.request.urlopen(url)
    bsobject = bs4.BeautifulSoup(html, 'lxml')
    
    table = str(bsobject)

    gammainfo = []

    """
    Extracting all table data from the BeautifulSoup object.
    """

    for i in range(len(table)):
        if table[i:i+8] == '<td>&lt;':
            for k in range(100):
                if table[i+8+k:i+8+k+3] == '<i>':
                    gammainfo.append(table[i+8:i+8+k].strip())
                    break
                elif table[i+8+k:i+8+k+5] == '</td>':
                    gammainfo.append(table[i+8:i+8+k].strip())
                    break
                
        elif table[i:i+5] == '<td>~':
            for k in range(100):
                if table[i+5+k:i+5+k+3] == '<i>':
                    gammainfo.append(table[i+5:i+5+k].strip())
                    break
                elif table[i+5+k:i+5+k+5] == '</td>':
                    gammainfo.append(table[i+5:i+5+k].strip())
                    break     
                
        elif table[i:i+4] == '<td>':
            for k in range(100):
                if table[i+4+k:i+4+k+3] == '<i>':
                    gammainfo.append(table[i+4:i+4+k].strip())
                    break
                elif table[i+4+k:i+4+k+5] == '</td>':
                    gammainfo.append(table[i+4:i+4+k].strip())
                    break  

    """
    Extracting all intensities and url addons from the table.
    """
                
    intensities = []
    for i in range(1,len(gammainfo),5):
        intensities.append(gammainfo[i])
  
    url_add_ons1 = []  
    for i in range(4,len(gammainfo),5):
        for j in range(100):
            if gammainfo[i][j:j+4] == 'href':
                url_add_ons1.append(gammainfo[i][j+4+2:])
                break
            
    url_add_ons2 = []           
    for i in range(len(url_add_ons1)):           
        for j in range(100):
            if url_add_ons1[i][j:j+2] == '><':
                url_add_ons2.append(url_add_ons1[i][0:j-1])
                break
            
        
    """
    Removing all intensities that are less than 1% and their corresponding 
    radionuclide url addon.
    """
    
    for i in range(len(intensities)):
        if intensities[i] == '':
            intensities[i] = 0
        intensities[i] = float(intensities[i])   
        if intensities[i] < 1:
            intensities[i] = 0
          
    
    indices = []
    for i,j in enumerate(intensities):
        if j == 0:
            indices.append(i)
            
    
    while 0 in intensities: intensities.remove(0)


    for i in indices:
        url_add_ons2[i] = 0
        
    
    while 0 in url_add_ons2: url_add_ons2.remove(0)        
    
    """
    Creating full urls.
    """ 
    
    urls = []
    for i in range(len(url_add_ons2)):
        urls.append('http://nucleardata.nuclear.lu.se/toi/' + url_add_ons2[i])
    
    
    
    return(intensities, urls)    
    


"""
gamma_extract takes in one url at a time from the gamma_search function and 
accesses the webpage of that radionuclide. It then extracts all gamma energies 
that have an intensity of at least 1% and also extracts the corresponding 
intensities as well. It also extracts the symbol of the radionuclide 
(including metastable states) as well as the atomic and mass numbers. Finally, 
the half life and decay constant are extracted as well. gamma_extract returns 
the gamma energies, corresponding intensities, symbol, atomic number, 
mass number, half life (in seconds), and decay constant (in seconds).
""" 


   
def gamma_extract(url):

    """
    Acquires significant gamma ray energies 
    (based on intensity being greater than 1%) and the corresponding intensity 
    of each gamma ray.
    """
    
    flag = False
    html = urllib.request.urlopen(url)
    bsobject = bs4.BeautifulSoup(html, 'lxml')
    bsgammatable = bsobject.table.findAll('table',{'border':'0',
                                                   'cellpadding':'0',
                                                   'cellspacing':'0'}, limit=1)

    table = str(bsgammatable)

    gammainfo = []


    for i in range(len(table)):
        if table[i:i+8] == '<td>&lt;':
            for k in range(20):
                if table[i+8+k:i+8+k+3] == '<i>':
                    gammainfo.append(table[i+8:i+8+k].strip())
                    break
                elif table[i+8+k:i+8+k+5] == '</td>':
                    gammainfo.append(table[i+8:i+8+k].strip())
                    break
                
        elif table[i:i+5] == '<td>~':
            for k in range(20):
                if table[i+5+k:i+5+k+3] == '<i>':
                    gammainfo.append(table[i+5:i+5+k].strip())
                    break
                elif table[i+5+k:i+5+k+5] == '</td>':
                    gammainfo.append(table[i+5:i+5+k].strip())
                    break     
                
        elif table[i:i+4] == '<td>':
            for k in range(20):
                if table[i+4+k:i+4+k+3] == '<i>':
                    gammainfo.append(table[i+4:i+4+k].strip())
                    break
                elif table[i+4+k:i+4+k+5] == '</td>':
                    gammainfo.append(table[i+4:i+4+k].strip())
                    break     
            
       
    for i in range(len(gammainfo)):
        if gammainfo[i] == '':
            gammainfo[i] = 0
        
        gammainfo[i] = float(gammainfo[i])
        
        if gammainfo[i] < float(1):
            if i%2 != 0:
                gammainfo[i] = 0 
                gammainfo[i-1] = 0
    
    
    while 0 in gammainfo: gammainfo.remove(0)
            
            
    gamma_energy = []
    gamma_intensity = []


    for i in range(len(gammainfo)):
        if (i+1)%2 == 0:
            gamma_intensity.append(gammainfo[i])
        else:
            gamma_energy.append(gammainfo[i])
    
    """
    Acquires the symbol of the radionuclide.
    """
    
    bsradionuclide = bsobject.find('caption',{'align':'top'})

    text = bsradionuclide.get_text()
    
    symbol = ''
        
    
    for i in range(len(text)):
        try:
            float(text[i])   
        except:
            symbol = symbol + text[i]

   
    symbol = symbol.strip()
    if symbol[0] == 'm':
        symbol = symbol.replace('m','')
        flag = True
        
    """
    Acquires the half life and the decay constant of the radionuclide.
    """
    
    index = table.index(symbol)
    
    #If flag equals True, then below conditional statement will append 'm' to
    #the beginning of the symbol to show that it is a metastable state of a
    #radionuclide.
    if flag == True:
        symbol = 'm' + symbol 
    

    for i in range(len(table)):
        if table[i:i+3] == '<i>':
            time_symbol = table[i-2]
            label = i-2
            break
    
    
    half_life_text = table[index+2:label].strip()
      
    half_life = float(half_life_text[1:])

    if time_symbol == 'm':
        half_life = 60*half_life
    elif time_symbol == 'h':
        half_life = 3600*half_life
    elif time_symbol == 'd': 
        half_life = 3600*24*half_life
    elif time_symbol == 'y':
        half_life = (3.154*10**7)*half_life
    
    decay_constant = (math.log(2))/(half_life)
    
    """
    Acquiring atomic number and mass number.
    """
    numbers = ''
    for i in range(len(url)):
        if url[i] == '=':
            numbers = numbers + url[i+1:]
            numbers = numbers
            mass_number = int(numbers[-3:])
            atomic_number = numbers[:-3]
            break
    
    #For mass number.    
    if mass_number > int(300):
        mass_number = mass_number - 300
    
    
    #For atomic number.
    if len(atomic_number) == 2:
        atomic_number = int(atomic_number[0])
    elif len(atomic_number) == 3:
        atomic_number = int(atomic_number[0:2])
    elif len(atomic_number) == 4:
        atomic_number = int(atomic_number[0:3])
    
    
    
    return(symbol, atomic_number, mass_number, half_life, decay_constant, 
           gamma_energy, gamma_intensity)    