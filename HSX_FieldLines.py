import numpy as np
import matplotlib.pyplot as plt

from flare import model
from flare.analysis import Fieldline
import math

# the model to load from the database
model.load("HSX/mgrid")
# model.load("HSX/hill_8_config")
probe_points = True
poloidal = False
calculate_distance = False

convert = False
# generate field line trace from (5.55, 0.8, 0) in steps of 1 deg in forward direction 
# for one toroidal turn (360 steps)
'''
Notes: 

===Currently Broken!===
The list of points to evaluate are not being evaluated.
This is a draft that preceeds the *working* 'coord_convert.py'
Ultimatly, this and coord_convert.py should be merged to remove functional redundancy.


coordinates should be larger -- meters scale HSX
coordinates in r, z, phi 
 (np.float64(1.3606240980048798), np.float64(0.08122268593174285), np.float64(0.2961466839515615))
 ^^^ correct coordingates A12TT 

 Do for all ports, and plot the ports in the figure. (labeld) 
 we want the distance between the field lines and the ports. 

'''


def cartesian_to_cylindrical(x, y, z, Deg=True, zero=True):
    """
    Converts Cartesian coordinates (x, y, z) to Cylindrical coordinates (r, z, phi).
    That is the format used by the Fieldlines.trace(..) module

    Phi is returned in radians.
    switch to degrees to do degrees, which is what HSX works with
    """
    r = math.sqrt(x**2 + y**2)
    if Deg == True: 
        if zero == True:
            phi = 0.0
        else:
            phi = math.degrees(math.atan2(y, x))
    else:
        if zero == True: 
            phi = 0.0
        else:
            phi = math.atan2(y, x)
    
    return r, z, phi

#############################################

ds = 1.0 / 180 * np.pi
# ds = 1e-
centroids_list = [
        
    (1.37013323, 0.06461841, 0.34234056),   # A12TT
    (1.5361697,  0.15705855, 0.18934832),   # A12MT 
    (1.54150325, 0.21199289, 0.08192894),   # A12MM
    (1.52012561,  0.25978317, -0.02803732), # A12MB
    (1.19444429, 0.21033671, 0.37424777),   # A23TT
    (1.36454599, 0.3237585,  0.31633814),   # A23MT
    (1.39608935, 0.38656896, 0.21893418),   # A23MM 
    (1.40813631, 0.43454497, 0.10776593),   # A23MB 
    (1.37853481,  0.41156213, -0.11067955), # A23BB 
    (1.37013323, -0.06461841, -0.34234056), # AP12BB
    (1.5361697,  -0.15705855, -0.18934832), # AP12MB 
    (1.54150325, -0.21199289, -0.08192894), # AP12MM
    (1.52012561, -0.25978317, 0.02803732 ), # AP12MT

    ]
import re

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
    (1.52012561, -0.25978317, 0.02803732, 'AP12MT')
]

coordinate_list_MGRID = [ 
    (1.3606240980048798, 0.08122268593174285, 0.2961466839515615), # this works 
    # (1.4905278814164387, 0.13664226820585382, 0.1893466855391248), # does not work
    (1.4958615005016325, 0.19157646193929104, 0.08193094190031343), #works
    (1.4744841654667222, 0.239366064661707, -0.02803880111092759), # works 
    (1.2055701300767918, 0.23463573120534428, 0.33198935449832945), #works               <--- This list describes which centroid points can be evaluated
    (1.329931513894172, 0.2971765112486623, 0.29194067773364835), # this works 
    (1.3614748313668232, 0.3599875493063812, 0.194536143204286), # works
    # (1.373521932711204, 0.4079642187626589, 0.08336698427973756), # does not work
    # (1.3674090770294978, 0.38726318530028775, -0.06842106505341472), #does not work 
    (1.3606240980048798, -0.08122268593174285, -0.2961466839515615), #works
    # (1.4905278814164387, -0.13664226820585382, -0.1893466855391248), # does not work
    (1.4958615005016325, -0.19157646193929104, -0.08193094190031343), #works
    (1.4744841654667222, -0.239366064661707, 0.02803880111092759), # works

    # (1.0014998,  0.48863193, 0.04729004), # This is the strike location from strikline calculator
    # (0.9992501,  0.4875452,  0.04062013), # this is the other listed strike location
    # (0.9892501,  0.4775452,  0.0362013),
     ]

poloidal_points = [ #the pink points
                [1.0373810529708862, 0.5059645175933838, 0.15366943180561066], # Magnetic center
                [1.0340561866760254, 0.5043584108352661, 0.14381198585033417], 
                [1.0307313203811646, 0.5027523636817932, 0.13395455479621887], 
                [1.0274064540863037, 0.5011462569236755, 0.12409710884094238], 
                [1.0240815877914429, 0.49954017996788025, 0.11423967033624649], 
                [1.020756721496582, 0.4979340732097626, 0.1043822318315506], 
                [1.0174318552017212, 0.4963279962539673, 0.0945247933268547], 
                [1.0141069889068604, 0.4947218894958496, 0.08466735482215881],
                [1.0107821226119995, 0.4931158125400543, 0.07480991631746292],
                [1.0074572563171387, 0.49150970578193665, 0.06495247781276703], # ouside the vessel after next point
                # [1.0041323900222778, 0.48990362882614136, 0.055095039308071136], 
                # [1.000807523727417, 0.4882975220680237, 0.045237600803375244], 
                # [0.9974827170372009, 0.4866914451122284, 0.03538016229867935], 
                # [0.9941578507423401, 0.4850853383541107, 0.02552272379398346], 
                # [0.9908329844474792, 0.48347926139831543, 0.015665285289287567], 
                # [0.9875081181526184, 0.48187315464019775, 0.005807845387607813], 
                # [0.9841832518577576, 0.48026707768440247, -0.0040495931170880795], 
                # [0.9808583855628967, 0.4786610007286072, -0.013907032087445259], 
                # [0.9775335192680359, 0.4770548939704895, -0.02376447059214115], 
                # [0.974208652973175, 0.4754488170146942, -0.03362191095948219],
                   
]

# Here are some blocks for quick testing: 

# for coord in coordinate_list_MGRID:
#     cx = coord[0]
#     cy = coord[1]
#     cz = coord[2]

# f = Fieldline.trace((1.3606240980048798, 0.08122268593174285, 0.2961466839515615), 1, ds, 360, coordinates='cartesian')

# f = Fieldline.trace((cx, cy, cz), 1, ds, 360, coordinates='cartesian')
# # visualize field line trace
# ax = plt.figure().add_subplot(projection='3d')
# ax.plot(f.x[0,:], f.x[1,:], f.x[2,:])
# plt.show()

coordinate_list_MGRID_CONVERTED = []
poloidal_CONVERTED = [] 


for x, y, z in coordinate_list_MGRID:
    (r, z, phi) = cartesian_to_cylindrical(x, y, z)
    coordinate_list_MGRID_CONVERTED.append((r, z, phi))

for x, y, z in poloidal_points:
    (r, z, phi) = cartesian_to_cylindrical(x, y, z)
    poloidal_CONVERTED.append((r, z, phi))
print('converted poloidal points: ')
print(f'len of list: {len(poloidal_CONVERTED)}')
print(poloidal_CONVERTED)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Below are the choices for what data set(s) to use

if probe_points == True:
    for cx, cy, cz in coordinate_list_MGRID_CONVERTED:
        f = Fieldline.trace((cx, cy, cz), 1, ds, 360,  coordinates='cartesian', direction='backward')
        ax.plot(f.x[0, :], f.x[1, :], f.x[2, :])

##############################
if poloidal == True: 
    for i in poloidal_CONVERTED:
        print(i)
    for cr, cz, cphi in poloidal_CONVERTED:
        f = Fieldline.trace((cr, cz, cphi), 1, ds, 360, stop_at_boundary=False, coordinates='cartesian', direction='backward')
        ax.plot(f.x[0, :], f.x[1, :], f.x[2, :])
##############################

for cx, cy, cz, label in centroids_list_with_labels:
    ax.scatter(cx, cy, cz, color='red', s=50, marker='o', label=label.split('(')[0].strip()) # Use scatter for points
    ax.text(cx, cy, cz, label.split('(')[0].strip(), color='blue') # Add text labels

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
# ax.set_title('Traced Field Lines')
ax.set_title('Traced Field Lines with Centroids')
plt.legend()

plt.show()
################################################################################################
################################################################################################
'''
controids (note that the 'problem' notation describes centroids that cannot be evaluated because they are out of B-field data range)

'A12'{
'TT': [1.37013323, 0.06461841, 0.34234056],
'MT': [1.5361697,  0.15705855, 0.18934832],     # problem 
'MM': [1.54150325, 0.21199289, 0.08192894], 
'MB': [1.52012561,  0.25978317, -0.02803732] },

'A23' : {
'TT': [1.19444429, 0.21033671, 0.37424777],
'MT': [1.36454599, 0.3237585,  0.31633814], 
'MM': [1.39608935, 0.38656896, 0.21893418], 
'MB': [1.40813631, 0.43454497, 0.10776593],     # problem 
'BB': [1.37853481,  0.41156213, -0.11067955] }, # problem 
   
'AP12' : {
'BB': [1.37013323, -0.06461841, -0.34234056], 
'MB': [1.5361697,  -0.15705855, -0.18934832],   # problem 
'MM': [1.54150325, -0.21199289, -0.08192894], 
'MT': [1.52012561, -0.25978317, 0.02803732 ] },
###

[1.37013323, 0.06461841, 0.34234056],
[1.5361697,  0.15705855, 0.18934832],   # problem 
[1.54150325, 0.21199289, 0.08192894], 
[1.52012561,  0.25978317, -0.02803732],
[1.19444429, 0.21033671, 0.37424777],
[1.36454599, 0.3237585,  0.31633814], 
[1.39608935, 0.38656896, 0.21893418], 
[1.40813631, 0.43454497, 0.10776593],   # problem 
[1.37853481,  0.41156213, -0.11067955], # problem 
[1.37013323, -0.06461841, -0.34234056], 
[1.5361697,  -0.15705855, -0.18934832], # problem 
[1.54150325, -0.21199289, -0.08192894], 
[1.52012561, -0.25978317, 0.02803732 ],

'''
################################################################################################
################################################################################################
# Distance calculator prototype: find the closest point along a field line to a port centroid
################################################################################################
if calculate_distance == True:
    # New figure for distance calcs
    fig2 = plt.figure(figsize=(12, 10))
    ax2 = fig2.add_subplot(projection='3d')

    # Collect all field line traces 
    all_field_lines_points = []

    # Retrace field lines and store all points
    for fl_idx, (cx, cy, cz) in enumerate(coordinate_list_MGRID):
        f = Fieldline.trace((cx, cy, cz), 1, ds, 360, coordinates='cartesian')
        all_field_lines_points.append(f.x) # Store the 3xN array of points
        ax2.plot(f.x[0, :], f.x[1, :], f.x[2, :], color='blue', alpha=0.7, label=f'Field Line {fl_idx+1}' if fl_idx == 0 else "") 

    # centroid coordinates and labels
    centroids_coords = [(c[0], c[1], c[2]) for c in centroids_list_with_labels]
    centroid_labels = [c[3].split('(')[0].strip() for c in centroids_list_with_labels]


    for cx, cy, cz, label in centroids_list_with_labels:
        ax2.scatter(cx, cy, cz, color='red', s=50, marker='o')
        ax2.text(cx, cy, cz, label.split('(')[0].strip(), color='black') # labels 
    # distance calculations 
    min_distance = float('inf')
    closest_field_line_point = None
    closest_centroid_coord = None
    closest_centroid_label = None
    closest_field_line_idx = -1
    closest_field_line_point_idx = -1

    for fl_idx, field_line_data in enumerate(all_field_lines_points):
        # field_line_data is a 3xN array (x,y,z coordinates)
        for point_idx in range(field_line_data.shape[1]):
            fl_point = field_line_data[:, point_idx] # current point (x,y,z) on the field line

            for c_idx, centroid_coord in enumerate(centroids_coords):
                distance = np.linalg.norm(fl_point - np.array(centroid_coord)) # Euclidean distance 

                if distance < min_distance:
                    min_distance = distance
                    closest_field_line_point = fl_point
                    closest_centroid_coord = centroid_coord
                    closest_centroid_label = centroid_labels[c_idx]
                    closest_field_line_idx = fl_idx
                    closest_field_line_point_idx = point_idx


    if closest_field_line_point is not None:
        ax2.scatter(closest_field_line_point[0], closest_field_line_point[1], closest_field_line_point[2], color='green', s=150, marker='X', label='Closest Field Line Point', zorder=10)

    if closest_centroid_coord is not None:
        ax2.scatter(closest_centroid_coord[0], closest_centroid_coord[1], closest_centroid_coord[2], color='purple', s=150, marker='o', label='Closest Port', zorder=10)


    if closest_field_line_point is not None and closest_centroid_coord is not None:
        ax2.plot([closest_field_line_point[0], closest_centroid_coord[0]],
                [closest_field_line_point[1], closest_centroid_coord[1]],
                [closest_field_line_point[2], closest_centroid_coord[2]],
                color='orange', linestyle='--', linewidth=2, label='Shortest Distance Link')

    ax2.set_xlabel('X axis')
    ax2.set_ylabel('Y axis')
    ax2.set_zlabel('Z axis')
    ax2.set_title('Field Lines and Centroids with Shortest Distance Highlighted')
    ax2.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

    print(f"\n==== Shortest Distance ====")
    print(f"The shortest distance found is: {min_distance:.6f}")
    print(f"This distance is between a point on Field Line #{closest_field_line_idx + 1} at coordinates: ") # field line numbers are in order of list appear.
    print(f"  X: {closest_field_line_point[0]:.6f}, Y: {closest_field_line_point[1]:.6f}, Z: {closest_field_line_point[2]:.6f}")
    print(f"and the port '{closest_centroid_label}' at coordinates: ")
    print(f"  X: {closest_centroid_coord[0]:.6f}, Y: {closest_centroid_coord[1]:.6f}, Z: {closest_centroid_coord[2]:.6f}")