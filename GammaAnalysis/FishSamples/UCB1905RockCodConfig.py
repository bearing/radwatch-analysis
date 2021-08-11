weight = 488.5 #g
vol = [184.7, 186.4, 190.7] #g
maxvol = 896 #g
source_energies = [605, 609, 662, 1460, 2614] #keV
source_halflives = [65128147.2, 1194, 951349665.6, 3.9356928 * (10 ** 18), 183.18] #s
time = 58492800 #s
tag = 0

params = {
    '605': [4, [[-2, -1], [-0.35, 1.5], [3, 4]]],
    '609': [5, [[-2, -1], [0.1, 1.5], [2, 4]]],
    '662': [5, [[-2, -1], [-0.5, 1.5], [2, 4]]],
    '1460': [15, [[-2, -1], [-0.5, 1], [1.5, 3]]],
    '2614': [20, [[-2, -1], [-0.5, 1], [1.5, 3]]],
}