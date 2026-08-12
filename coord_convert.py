
'''
Coordiante converter and Port Determination

    This program takes in a list of fieldline starting points
     -- In this case the points are in a line from the center of 
        the magnetic axis [normal mgrid equi3d file]) to the strikline point,
        which was determined by inspection of Fig 13 in 
        'HSX as an example of a resilient non-resonant divertor' by A. Bader et al. 
    and uses flare's 
    Fieldline.trace((r, z, phi), 1, ds, 360, stop_at_boundary=False, coordinates='cartesian', direction='backward/foreward')
    to trace magnetic fieldlines around the vessel.

    The starting points of the traced points are green.
    The midpoint of each fieldline is purple. 
    
    HSX port centroids are red points, and are labled.


The intended use of this program is to find a port that is close to the initial strike location
    which is [0.45, 3.5] = [Tor. Angle (radians), Pol. Angle (radians)],
    with the toroidal angle measured from the center of HSX from the x axis (A00) 
    and Poloidal measued from the center of the magnetic axis. 
    -- Calcualtions for this point can be found in 'Strikline_Calculator.py'
and a port that is close to the midpoint of the field line. 

(currently) by inspection we can determine what ports are suitable. 

-Maxwell Loughan  7/23/26
'''
import pyvista as pv
import numpy as np
from moose import geometry
from flare import model
from flare.analysis import bfield
import math
import matplotlib.pyplot as plt

from flare.analysis import Fieldline

np.set_printoptions(legacy='1.25') 

ds = 1.0 / 180 * np.pi

# model to evaluate 
model.load("HSX/qhs/mgrid") # model 1
# model.load("HSX/hill_8_config") #model 2


bfield_eval = False
fieldline_eval = True
poloidal_points = [ #the pink points
                [1.0373810529708862, 0.5059645175933838, 0.15366943180561066], # Magnetic center
                [1.0340561866760254, 0.5043584108352661, 0.14381198585033417], 
                [1.0307313203811646, 0.5027523636817932, 0.13395455479621887], 
                [1.0274064540863037, 0.5011462569236755, 0.12409710884094238], 
                [1.0240815877914429, 0.49954017996788025, 0.11423967033624649], 
                [1.020756721496582, 0.4979340732097626, 0.1043822318315506], 
                [1.0174318552017212, 0.4963279962539673, 0.0945247933268547], 
                [1.0141069889068604, 0.4947218894958496, 0.08466735482215881],
                [1.0107821226119995, 0.4931158125400543, 0.07480991631746292], # last trace that makes it all the way around the vessel
                [1.0074572563171387, 0.49150970578193665, 0.06495247781276703], # second shortest trace
                [1.0041323900222778, 0.48990362882614136, 0.055095039308071136], # shortest trace before the strike point

                ## These are high resolution evauluation points as we get closer to the strike
                [1.00376296043396, 0.48972517251968384, 0.053999768363104925], 
                [1.003393530845642, 0.4895467162132263, 0.05290449741813871], 
                [1.0030241012573242, 0.4893682599067688, 0.05180922647317251], 
                [1.0026546716690063, 0.4891898036003113, 0.050713955528206296], 
                [1.0022852420806885, 0.48901134729385376, 0.049618684583240084], 
                [1.0019158124923706, 0.48883289098739624, 0.04852341363827387], 
                [1.0015463829040527, 0.4886544346809387, 0.04742814269330767], # closest we can get to strike point --- VERY strange trace

                # [1.000807523727417, 0.4882975220680237, 0.045237600803375244], # STRIKE POINT ; problems with tracing here
                

                #           OUTSIDE VESSEL (ignore)
                # [0.9974827170372009, 0.4866914451122284, 0.03538016229867935], 
                # [0.9941578507423401, 0.4850853383541107, 0.02552272379398346], 
                # [0.9908329844474792, 0.48347926139831543, 0.015665285289287567], 
                # [0.9875081181526184, 0.48187315464019775, 0.005807845387607813], 
                # [0.9841832518577576, 0.48026707768440247, -0.0040495931170880795], 
                # [0.9808583855628967, 0.4786610007286072, -0.013907032087445259], 
                # [0.9775335192680359, 0.4770548939704895, -0.02376447059214115], 
                # [0.974208652973175, 0.4754488170146942, -0.03362191095948219],
                   
]
    # (1.0014998,  0.48863193, 0.04729004), # This is the strike location from strikline calculator
    # (0.9992501,  0.4875452,  0.04062013), # this is the other listed strike location (outside vessel)
centroids_list_with_labels = [
    (1.37013323, 0.06461841, 0.34234056, 'A12TT'),
    (1.5361697,  0.15705855, 0.18934832, 'A12MT'),
    (1.54150325, 0.21199289, 0.08192894, 'A12MM'),
    (1.52012561,  0.25978317, -0.02803732, 'A12MB'),
    (1.19444429, 0.21033671, 0.37424777, 'A23TT'),
    (1.36454599, 0.3237585,  0.31633814, 'A23MT'),
    (1.39608935, 0.38656896, 0.21893418, 'A23MM'),
    (1.40813631, 0.43454497, 0.10776593, 'A23MB'),
    (1.37853481,  0.41156213, -0.11067955, 'A23BB'),
    (1.37013323, -0.06461841, -0.34234056, 'AP12BB'),
    (1.5361697,  -0.15705855, -0.18934832, 'AP12MB'),
    (1.54150325, -0.21199289, -0.08192894, 'AP12MM'),
    (1.52012561, -0.25978317, 0.02803732, 'AP12MT'),
]
total_centroids_list_with_labels = [
    #A
    # (1.37013323, 0.06461841, 0.34234056, 'A12TT'),
    # (1.5361697,  0.15705855, 0.18934832, 'A12MT'),
    # (1.54150325, 0.21199289, 0.08192894, 'A12MM'),
    # (1.52012561,  0.25978317, -0.02803732, 'A12MB'),
    # (1.19444429, 0.21033671, 0.37424777, 'A23TT'),
    # (1.36454599, 0.3237585,  0.31633814, 'A23MT'),
    # (1.39608935, 0.38656896, 0.21893418, 'A23MM'),
    (1.40813631, 0.43454497, 0.10776593, 'A23MB'),
    (1.37853481,  0.41156213, -0.11067955, 'A23BB'),
    (1.20455327, 0.51165693, 0.2771323, 'A34MT'),
    (0.76632101, 0.62503774, 0.25787352, 'A56TT'),
    (1.03310999, 0.80307657, 0.00374969, 'A56MB'),
    (0.74949781, 0.42783281, 0.03118502, 'A56IN'),
    # A PRIME
    # (1.37013323, -0.06461841, -0.34234056, 'AP12BB'),
    # (1.5361697,  -0.15705855, -0.18934832, 'AP12MB'),
    # (1.54150325, -0.21199289, -0.08192894, 'AP12MM'),
    # (1.52012561, -0.25978317, 0.02803732, 'AP12MT'),
    # (1.37013323, -0.06461841, -0.34234056, 'AP23BB'),
    # (1.5361697,  -0.15705855, -0.18934832, 'AP23MB'),
    # (0.38656896,  1.39608935, -0.21893418, 'AP23MM'),
    # (0.43454497,  1.40813631, -0.10776593, 'AP23MT'),
    # (0.41156213, 1.37853481, 0.11067955, 'AP23TT'),
    # (0.51165693,  1.20455327, -0.2771323 , 'AP34MB'),
    # (0.62503774,  0.76632101, -0.25787352, 'AP56BB'),
    # (0.80307657,  1.03310999, -0.00374969, 'AP56MT'),
    # (0.42783281,  0.74949781, -0.03118502, 'AP56IN'),
    # B
    # (-0.06461841, 1.37013323, 0.34234056, 'B12TT'),
    # (-0.15705855, 1.5361697, 0.18934832, 'B12MT'),
    # (-0.21199289, 1.54150325, 0.08192894, 'B12MM'),
    # (-0.25978317, 1.52012561, -0.02803732, 'B12MB'),
    # (-0.21033671, 1.19444429, 0.37424777, 'B23TT'),
    # (-0.3237585, 1.36454599, 0.31633814, 'B23MT'),
    # (-0.38656896, 1.39608935, 0.21893418, 'B23MM'),
    # (-0.43454497, 1.40813631, 0.10776593, 'B23MB'),
    # (-0.41156213, 1.37853481, -0.11067955, 'B23BB'),
    # (-0.51165693, 1.20455327, 0.2771323, 'B34MT'),
    # (-0.62503774, 0.76632101, 0.25787352, 'B56TT'),
    (-0.80307657, 1.03310999, 0.00374969, 'B56MB'),
    (-0.42783281, 0.74949781, 0.03118502, 'B56IN'),
    # B PRIME
    (0.06461841, 1.37013323, -0.34234056, 'BP12BB'),
    (0.15705855, 1.5361697, -0.18934832, 'BP12MB'),
    (0.21199289, 1.54150325, -0.08192894, 'BP12MM'),
    (0.25978317, 1.52012561, 0.02803732, 'BP12MT'),
    (0.21033671, 1.19444429, -0.37424777, 'BP23BB'),
    (0.3237585, 1.36454599, -0.31633814, 'BP23MB'),
    (0.38656896, 1.39608935, -0.21893418, 'BP23MM'),
    (0.43454497,  1.40813631, -0.10776593, 'BP23MT'),
    (0.41156213, 1.37853481, 0.11067955, 'BP23TT'),
    (0.51165693, 1.20455327, -0.2771323, 'BP34MB'),
    (0.62503774, 0.76632101, -0.25787352, 'BP56BB'),
    ( 0.80307657,  1.03310999, -0.00374969, 'BP56MT'),
    (0.42783281,  0.74949781, -0.03118502, 'BP56IN'),
    # # C
    # (-1.37013323, -0.06461841,  0.34234056, 'C12TT'),
    # (-1.5361697, -0.15705855, 0.18934832, 'C12MT'),
    # (-1.54150325, -0.21199289,  0.08192894, 'C12MM'),
    # (-1.52012561, -0.25978317, -0.02803732, 'C12MB'),
    # (-1.19444429, -0.21033671,  0.37424777, 'C23TT'),
    # (-1.36454599, -0.3237585,   0.31633814, 'C23MT'),
    # (-1.39608935, -0.38656896,  0.21893418, 'C23MM'),
    # (-1.40813631, -0.43454497,  0.10776593, 'C23MB'),
    # (-1.37853481, -0.41156213, -0.11067955, 'C23BB'),
    (-1.20455327, -0.51165693,  0.2771323, 'C34MT'),
    (-0.76632101, -0.62503774,  0.25787352, 'C56TT'),
    (-1.03310999, -0.80307657,  0.00374969, 'C56MB'),
    (-0.74949781, -0.42783281,  0.03118502, 'C56IN'),
    # C PRIME
    # (-1.37013323,  0.06461841, -0.34234056, 'CP12BB'),
    # (-1.5361697,   0.15705855, -0.18934832, 'CP12MB'),
    # (-1.54150325,  0.21199289, -0.08192894, 'CP12MM'),
    # (-1.54150325,  0.21199289, -0.08192894, 'CP12MT'),
    # (-1.19444429,  0.21033671, -0.37424777, 'CP23BB'),
    # (-1.36454599,  0.3237585,  -0.31633814, 'CP23MB'),
    # (-1.39608935,  0.38656896, -0.21893418, 'CP23MM'),
    # (-1.40813631,  0.43454497, -0.10776593, 'CP23MT'),
    # (-1.38382745,  0.40851835,  0.11304774, 'CP23TT'),
    (-1.20455327,  0.51165693, -0.2771323, 'CP34MB'),
    (-0.76632101,  0.62503774, -0.25787352, 'CP56BB'),
    (-1.03310999,  0.80307657, -0.00374969, 'CP56MT'),
    (-0.74949781,  0.42783281, -0.03118502, 'CP56IN'),
    # # D
    # (0.06461841, -1.37013323,  0.34234056, 'D12TT'),
    # (0.15705855, -1.5361697,   0.18934832, 'D12MT'),
    # (0.21199289, -1.54150325,  0.08192894, 'D12MM'),
    # (0.25978317, -1.52012561, -0.02803732, 'D12MB'),
    # (0.21033671, -1.19444429,  0.37424777, 'D23TT'),
    # (0.3237585,  -1.36454599,  0.31633814, 'D23MT'),
    # (0.38656896, -1.39608935,  0.21893418, 'D23MM'),
    # (0.43454497, -1.40813631,  0.10776593, 'D23MB'),
    # (0.41156213, -1.37853481, -0.11067955, 'D23BB'),
    # (0.51165693, -1.20455327 , 0.2771323, 'D34MT'),
    # (0.62503774, -0.76632101,  0.25787352, 'D56TT'),
    # (0.80307657, -1.03310999,  0.00374969, 'D56MB'),
    # (0.42783281, -0.74949781,  0.03118502, 'D56IN'),
    # # D PRIME
    # (-0.06461841, -1.37013323, -0.34234056, 'DP12BB'),
    # (-0.15705855, -1.5361697,  -0.18934832, 'DP12MB'),
    # (-0.21199289, -1.54150325, -0.08192894, 'DP12MM'),
    # (-0.25978317, -1.52012561,  0.02803732, 'DP12MT'),
    # (-0.21033671, -1.19444429, -0.37424777, 'DP23BB'),
    # (-0.3237585,  -1.36454599, -0.31633814, 'DP23MB'),
    # (-0.38656896, -1.39608935, -0.21893418, 'DP23MM'),
    # (-0.43454497, -1.40813631, -0.10776593, 'DP23MT'),
    # (-0.41156213, -1.37853481,  0.11067955, 'DP23TT'),
    # (-0.51165693, -1.20455327, -0.2771323 , 'DP34MB'),
    # (-0.62503774, -0.76632101, -0.25787352, 'DP56BB'),
    # (-0.80307657, -1.03310999, -0.00374969, 'DP56MT'),
    # (-0.42783281, -0.74949781, -0.03118502, 'DP56IN'),
]
def cartesian_to_cylindrical(x, y, z, Deg=False):
    """
    Converts Cartesian coordinates (x, y, z) to Cylindrical coordinates (r, z, phi).
    That is the format used by the Fieldlines.trace(..) module

    Phi is returned in radians.
    switch to degrees to do degrees, which is what HSX works with
    """
    r = math.sqrt(x**2 + y**2)
    if Deg == True: 
        phi = math.degrees(math.atan2(y, x))
    else:
        phi = math.atan2(y, x)
    
    return r, z, phi
testtt = cartesian_to_cylindrical(1.0373810529708862, 0.5059645175933838, 0.15366943180561066)
print(f" theconverted centerline points in cart to cyl are ::::: {testtt}")

poloidal_CONVERTED = [] 

for x, y, z in poloidal_points:
    (r, z, phi) = cartesian_to_cylindrical(x, y, z)
    poloidal_CONVERTED.append((r, z, phi))
print('converted poloidal points: ')
print(f'len of list: {len(poloidal_CONVERTED)}')
print(poloidal_CONVERTED[0])

# if bfield_eval == True:
#     print(" ::::B-FIELD EVAL::::" )
#     for r, z, phi in poloidal_CONVERTED:
#         bfield_eval = bfield.eval(r, z, phi)
#         print(bfield_eval)

plot_plot = True 
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# plotting the start points for the fieldline trace
x_coords, y_coords, z_coords = zip(*poloidal_points)
ax.scatter(x_coords, y_coords, z_coords, color='green', marker='o', s=50)

forward = False
find_halfway = True
find_closest_port = False

if fieldline_eval == True: 
    print(" ::::FIELD-LINE EVAL::::" )
    field_line_index = 0
    for r, z, phi in poloidal_CONVERTED:
    # for r, z, phi in poloidal_CONVERTED[-5:]:
        field_line_index += 1
        print(f"Field Line {field_line_index}")
        if forward == True: 
            f =Fieldline.trace((r, z, phi), 1, ds, 360, stop_at_boundary=False, coordinates='cartesian', direction='forward')
        else:
            f =Fieldline.trace((r, z, phi), 1, ds, 360, stop_at_boundary=False, coordinates='cartesian', direction='backward')
            print(f"the f line is : {f}")
        if find_halfway == True:
            x_line_middle = len(f.x[0, :]) // 2
            y_line_middle = len(f.x[1, :]) // 2
            z_line_middle = len(f.x[2, :]) // 2
            print(f'Middle of field line trace []: {(f.x[0, :][-1], f.x[1, :][-1], f.x[2, :][-1])}') # all the x, y, and z coords
            ax.scatter(f.x[0, :][x_line_middle], f.x[1, :][y_line_middle], f.x[2, :][z_line_middle], color='purple', s=50, marker='o')
        if find_closest_port == True:
            pass # will want to impliment some code to find the closest port
        ax.plot(f.x[0, :], f.x[1, :], f.x[2, :])

all_ports_show = True

if plot_plot == True:
    if all_ports_show == True: 

        for cx, cy, cz, label in total_centroids_list_with_labels: # change back to centroids_list_with_labels
            ax.scatter(cx, cy, cz, color='red', s=50, marker='o', label=label.split('(')[0].strip()) # Use scatter for points
            ax.text(cx, cy, cz, label.split('(')[0].strip(), color='blue') # Add text labels
        plt.show()
    else:
        for cx, cy, cz, label in centroids_list_with_labels: # change back to centroids_list_with_labels
                ax.scatter(cx, cy, cz, color='red', s=50, marker='o', label=label.split('(')[0].strip()) # Use scatter for points
                ax.text(cx, cy, cz, label.split('(')[0].strip(), color='blue') # Add text labels
        plt.show()
