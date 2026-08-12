'''
CONFIG SCRIPT TO BE IMPORTED INTO MAIN HSX MAGNETIC EVAL SCRIPT FOR COMPARISON

THIS IS FOR THE (alt) hill_8_config FILE (MODEL 2)

The other file (model 1) is for the mgrid file at HSX/mgrid

-Maxwell Loughan

'''
name_of_script = 'hill_8 config file'
final_B = 'not chosen'

import sys

import pyvista as pv
import numpy as np
from moose import geometry
from flare import model
from flare.analysis import bfield
# probe_length = 0.05
# Activate verbose mode
verbose = True
InteractiveMode = False # interactive STL selection tool mode

# Set up a list to temp. catch the point selections
# Click history centroids
ClickedCentroids = []
# pv.set_jupyter_backend('trame') # attempt to get this to run with GPU -- ignore

########### LIST of PORTS ################
port_dict = {
    'A12' : {'TT': [1.37013323, 0.06461841, 0.34234056],'MT': [1.5361697,  0.15705855, 0.18934832], 'MM': [1.54150325, 0.21199289, 0.08192894], 'MB': [1.52012561,  0.25978317, -0.02803732] },
    'A23' : {'TT': [1.19444429, 0.21033671, 0.37424777],'MT': [1.36454599, 0.3237585,  0.31633814], 'MM': [1.39608935, 0.38656896, 0.21893418], 'MB': [1.40813631, 0.43454497, 0.10776593], 'BB': [1.37853481,  0.41156213, -0.11067955] },
    'A34' : {'MT': [1.20455327, 0.51165693, 0.2771323]},
    'A45' : {},
    'A56' : {'TT': [0.76632101, 0.62503774, 0.25787352], 'MB': [1.03310999, 0.80307657, 0.00374969], 'IN': [0.74949781, 0.42783281, 0.03118502] },
    # COnvention with AP :: A:[x,y,z] -> AP:[]
    'AP12' : {'BB': [1.37013323, -0.06461841, -0.34234056], 'MB': [1.5361697,  -0.15705855, -0.18934832], 'MM': [1.54150325, -0.21199289, -0.08192894], 'MT': [1.52012561, -0.25978317, 0.02803732 ] },
    'AP23' : {'BB': [0.21033671,  1.19444429, -0.37424777], 'MB': [0.3237585,  1.36454599, -0.31633814 ], 'MM': [0.38656896,  1.39608935, -0.21893418], 'MT': [0.43454497,  1.40813631, -0.10776593], 'TT': [0.41156213, 1.37853481, 0.11067955] },
    'AP34' : {'MB': [0.51165693,  1.20455327, -0.2771323 ]},
    'AP45' : {},
    'AP56' : {'BB': [0.62503774,  0.76632101, -0.25787352], 'MT': [0.80307657,  1.03310999, -0.00374969], 'IN': [0.42783281,  0.74949781, -0.03118502] },
    ###
    'B12' : {'TT': [-0.06461841, 1.37013323, 0.34234056],'MT': [-0.15705855, 1.5361697, 0.18934832,], 'MM': [-0.21199289, 1.54150325, 0.08192894], 'MB': [-0.25978317, 1.52012561, -0.02803732]},
    'B23' : {'TT': [-0.21033671, 1.19444429, 0.37424777],'MT': [-0.3237585, 1.36454599, 0.31633814,], 'MM': [-0.38656896, 1.39608935, 0.21893418], 'MB': [-0.43454497, 1.40813631, 0.10776593], 'BB': [-0.41156213, 1.37853481, -0.11067955] },
    'B34' : {'MT': [-0.51165693, 1.20455327, 0.2771323 ]},
    'B45' : {},
    'B56' : {'TT': [-0.62503774, 0.76632101, 0.25787352], 'MB': [-0.80307657, 1.03310999, 0.00374969], 'IN': [-0.42783281, 0.74949781, 0.03118502]},

    'BP12' : {'BB': [0.06461841, 1.37013323, -0.34234056 ],'MB': [0.15705855, 1.5361697, -0.18934832], 'MM': [0.21199289, 1.54150325, -0.08192894], 'MT': [0.25978317, 1.52012561, 0.02803732]},
    'BP23' : {'BB': [0.21033671, 1.19444429, -0.37424777],'MB': [0.3237585, 1.36454599, -0.31633814], 'MM': [0.38656896, 1.39608935, -0.21893418], 'MT': [0.43454497,  1.40813631, -0.10776593], 'TT': [0.41156213, 1.37853481, 0.11067955]},
    'BP34' : {'MB': [0.51165693, 1.20455327, -0.2771323]},
    'BP45' : {},
    'BP56' : {'BB': [0.62503774, 0.76632101, -0.25787352], 'MT': [ 0.80307657,  1.03310999, -0.00374969], 'IN': [ 0.42783281,  0.74949781, -0.03118502]},
    ### Conventions with C :: 
    'C12' : {'TT': [-1.37013323, -0.06461841,  0.34234056],'MT': [-1.5361697, -0.15705855, 0.18934832], 'MM': [-1.54150325, -0.21199289,  0.08192894], 'MB': [-1.52012561, -0.25978317, -0.02803732]},
    'C23' : {'TT': [-1.19444429, -0.21033671,  0.37424777],'MT': [-1.36454599, -0.3237585,   0.31633814], 'MM': [-1.39608935, -0.38656896,  0.21893418], 'MB': [-1.40813631, -0.43454497,  0.10776593], 'BB': [-1.37853481, -0.41156213, -0.11067955] },
    'C34' : {'MT': [-1.20455327, -0.51165693,  0.2771323 ]},
    'C45' : {},
    'C56' : {'TT': [-0.76632101, -0.62503774,  0.25787352], 'MB': [-1.03310999, -0.80307657,  0.00374969], 'IN': [-0.74949781, -0.42783281,  0.03118502]},

    'CP12' : {'BB': [-1.37013323,  0.06461841, -0.34234056],'MB':  [-1.5361697,   0.15705855, -0.18934832], 'MM': [-1.54150325,  0.21199289, -0.08192894], 'MT': [-1.54150325,  0.21199289, -0.08192894]},
    'CP23' : {'BB': [-1.19444429,  0.21033671, -0.37424777],'MB': [-1.36454599,  0.3237585,  -0.31633814], 'MM': [-1.39608935,  0.38656896, -0.21893418], 'MT': [-1.40813631,  0.43454497, -0.10776593], 'TT':  [-1.38382745,  0.40851835,  0.11304774]}, # centroid problem on TT : offcenter (instead click rim) 
    'CP34' : {'MB': [-1.20455327,  0.51165693, -0.2771323 ]},                                                                                                                                                                                                                           # COULD BE A MASSIVE PROBLEM !!!
    'CP45' : {},
    'CP56' : {'BB': [-0.76632101,  0.62503774, -0.25787352], 'MT': [-1.03310999,  0.80307657, -0.00374969], 'IN': [-0.74949781,  0.42783281, -0.03118502]},
    ###
    'D12' : {'TT': [ 0.06461841, -1.37013323,  0.34234056],'MT': [ 0.15705855, -1.5361697,   0.18934832], 'MM': [ 0.21199289, -1.54150325,  0.08192894], 'MB':  [ 0.25978317, -1.52012561, -0.02803732]},
    'D23' : {'TT': [ 0.21033671, -1.19444429,  0.37424777],'MT': [ 0.3237585,  -1.36454599,  0.31633814], 'MM': [ 0.38656896, -1.39608935,  0.21893418], 'MB': [ 0.43454497, -1.40813631,  0.10776593], 'BB': [ 0.41156213, -1.37853481, -0.11067955] },
    'D34' : {'MT': [ 0.51165693, -1.20455327 , 0.2771323 ]},
    'D45' : {},
    'D56' : {'TT': [ 0.62503774, -0.76632101,  0.25787352], 'MB':  [ 0.80307657, -1.03310999,  0.00374969], 'IN': [ 0.42783281, -0.74949781,  0.03118502]},

    'DP12' : {'BB': [-0.06461841, -1.37013323, -0.34234056] ,'MB': [-0.15705855, -1.5361697,  -0.18934832], 'MM': [-0.21199289, -1.54150325, -0.08192894], 'MT': [-0.25978317, -1.52012561,  0.02803732]},
    'DP23' : {'BB': [-0.21033671, -1.19444429, -0.37424777] ,'MB': [-0.3237585,  -1.36454599, -0.31633814], 'MM': [-0.38656896, -1.39608935, -0.21893418], 'MT': [-0.43454497, -1.40813631, -0.10776593], 'TT': [-0.41156213, -1.37853481,  0.11067955] },
    'DP34' : {'MB': [-0.51165693, -1.20455327, -0.2771323 ]},
    'DP45' : {},
    'DP56' : {'BB': [-0.62503774, -0.76632101, -0.25787352], 'MT': [-0.80307657, -1.03310999, -0.00374969], 'IN': [-0.42783281, -0.74949781, -0.03118502]},
}
'''
NOTES: 

There is a centroid problem where one of the top ports (commented above) has a centrpoid that is actually NOT in the middle of the port 
The actual centroid can (seemingly) be determined by clicking on the rim (however, the rim might be raided...)

This is due to the the arrangement of the pannels on the port opening. 
Maybe look to see if there are the same number of pannels on the port openings with the off-center centroid.
then you could make a function that handles things differently to accomidate? 

-max
'''
####################################################

# HSX Mesh STL
stl_mesh = pv.read("HSX_ASSEMBLY_RECONSTRUCTED.STL")
# Wall surface from moose geometry 
wall_grids = geometry.Torosurf.loadtxt("./wall_3cm_from_plasma_full.txt").grid.vtk()

# Convert the first structured grid to a surface PolyData geometry
wall_pv = pv.wrap(wall_grids[0])
wall_surface = wall_pv.extract_surface()

# Interactive plotting environment
plotter = pv.Plotter()
plotter.background_color = "black"

plotter.add_mesh( #Mesh for HSX
    stl_mesh,
    # style="wireframe",
    color="spring_green",
    label="HSX Assembly",
    opacity=0.3
)

plotter.add_mesh( #Mesh for wall surface (assuming that this is the plasma edge)
    wall_surface,
    color="purple",
    label="Wall Surface",
    opacity=0.9
)


# Initialize external field configurations
# Here we should be able to put in a model to work with 
    # Note: Location of file on Max's Windows laptop running WSL in VScode
    # \\wsl.localhost\Ubuntu\home\madmax\DATABASE\flare\HSX\
    # drop files in here with the configurations, and everything should work!
        
#model.load("HSX/QHS_with_coils")
# model.load("HSX/mgrid") # model 1 
model.load("HSX/hill_8_config") # model 2

# Find cell normals to capture true flat face orientations
mesh = stl_mesh.compute_normals(cell_normals=True, point_normals=False, inplace=False)

# Container list for the normal (probe) arrow
current_arrow = [None]
# Container list for flat surface visuals  
active_actors = []

def my_callback(point):

    #Centroid of Port Determination
    
    # Clear previous highlights from the screen
    for actor in active_actors:
        plotter.remove_actor(actor)
    active_actors.clear()

    # id a seed cell to use nearest to the clicked point
    seed_cell_id = mesh.find_closest_cell(point)
    if seed_cell_id == -1:
        return
    seed_normal = mesh.cell_normals[seed_cell_id]

    # Using a flood-fill method, identifiy a flat area to find the centroid
    # We are going to set the angle tolerance between cells to 5 deg 
    angle_tolerance_deg = 5.0  
    cos_tolerance = np.cos(np.radians(angle_tolerance_deg))

    # By finding cells next to the slected cell, we can deterimine
    # the number of flat cells, and add them to a list

    visited = set() # create an empty set to append to later for neighbors
    queue = [seed_cell_id] # queue list 
    visited.add(seed_cell_id) # visitied cells

    flat_cell_ids = [] # list for the flat surface catalog

    # Flood-fill surface determination
    # We make a loop that checks neighboring cells for angular similarity 
    while queue:
        current_cell = queue.pop(0) # remove and return the first element (queue)
        flat_cell_ids.append(current_cell)
        
        # Neighbors are cells that share an edge in the mesh
        neighbors = mesh.cell_neighbors(current_cell, connections="edges")
        
        for neighbor in neighbors:
            if neighbor not in visited:

                neighbor_normal = mesh.cell_normals[neighbor]
                # Use dot product to check if the neighbor normal points the same direction
                dot_product = np.dot(seed_normal, neighbor_normal)

                if dot_product >= cos_tolerance:
                    visited.add(neighbor)
                    queue.append(neighbor)
    
    # Now we can compute the centroid of the flat reigion 
    # Extract the flat reigion
    flat_region_mesh = mesh.extract_cells(flat_cell_ids)

    # Compute the ave. positions of the cell centers 
    cell_centers = flat_region_mesh.cell_centers().points
    region_centroid = np.mean(cell_centers, axis=0) # This is ideally the WISP probe position

    # Highlight the flat area
    region_actor = plotter.add_mesh(
        flat_region_mesh, 
        color="light blue", 
        show_edges=True, 
        line_width=1, 
        name="highlighted_flat_region"
    )
    # Store actor(s) to handle removal on next click
    active_actors.extend([region_actor])

    # B-feild Evaluation at Centroid and Data Display
    bfield_eval = bfield.eval(region_centroid[0], region_centroid[1], region_centroid[2])
    if verbose == True:print(f"\n--- Selection Registered ---")
    if verbose == True: print(f"Clicked coordinate: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}]")
    if verbose == True:print(f"Flat region includes {len(flat_cell_ids)} cells.")
    if verbose == True:print(f"Port centroid coordinates: {region_centroid}")
    if verbose == True:print(f"B-field at centroid of port opening (flat face): {bfield_eval}")
    
    # this is a temp. way to append the clicked centoids to the list to get port IDs
    ClickedCentroids.extend([region_centroid])

    # Index of the specific triangular centroid
    cell_index = mesh.find_closest_cell(region_centroid)
    
    # Normal vector array to the cell centroid
    raw_normal = mesh['Normals'][cell_index]
    
    # Invert the vector direction to point inward toward the internal volume
    inward_normal = raw_normal * -1
    if verbose == True: print(f"Inward Face Normal (vector of WISP Gauge extension): [{inward_normal[0]:.4f}, {inward_normal[1]:.4f}, {inward_normal[2]:.4f}]")
    
    # Erase the previous arrow actor
    if current_arrow[0] is not None:
        plotter.remove_actor(current_arrow[0])
        
    # Position the vector arrow on the centroid
    # Scale to 0.05 assuming mesh is in meters (5 cm probe length)
    probe_length = 0.05 ###################### PLEASE VERIFY ###########################
    # while True:
    #     try: 
    #         probe_length = float(input("What probe length (0.05 m default)? : "))
    #         break
    #     except ValueError:
    #         print('Input an integer or decimal')

    arrow_mesh = pv.Arrow(start=region_centroid, direction=inward_normal, scale= probe_length) 
    
    # Evaluate the magnetic feild at the probe tip 
    # -> Add the normal vector to the centroid point to make new point at tip of vector
    #   -> Evaluate B-feild at point that is at tip of vector
    ProbeTip_B = bfield.eval((region_centroid[0] + (probe_length * inward_normal[0])), (region_centroid[1] + (probe_length * inward_normal[1])), (region_centroid[2] + (probe_length * inward_normal[2])))
    if verbose == True: print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")
    # Add arrow to plotter and track via container list index
    current_arrow[0] = plotter.add_mesh(arrow_mesh, color='red', label="Inward Normal Vector")

# We will separate things out into quadrants to make selection easy
# starting from the loaded front facing quandrant and moving CW

    # 
    print(f"B feild : {ProbeTip_B}")
    global final_B
    final_B = ProbeTip_B

########### In-Terminal User Interface (non-Visual) ################################
def PortSelector(portnumber): # inut whould be of format : [x, y, z] (assuming cartisian coords)
    port_output = my_callback(portnumber)
    return port_output


def DoEval(chosen_port):
    
    try: 
        PortString = str(chosen_port)
        if PortString[1] == 'P':
            quadrant_interval = PortString[0] + PortString[1] + PortString[2] + PortString[3]
            if verbose == True: print(f'Quadrant_interval = {quadrant_interval}')
            port_position = PortString[4] + PortString[5]
            if verbose == True: print(f'Position = {port_position}')
            port_coords = port_dict[quadrant_interval][port_position]
            if verbose == True: print(f"Selected port coordinates: {port_coords}")
            PortSelector(port_coords)
        else:

            quadrant_interval = PortString[0] + PortString[1] + PortString[2] 
            if verbose == True: print(f'Quadrant_interval = {quadrant_interval}')
            port_position = PortString[3] + PortString[4]
            if verbose == True: print(f'Position = {port_position}')
            port_coords = port_dict[quadrant_interval][port_position]
            if verbose == True: print(f"Selected port coordinates: {port_coords}")
            PortSelector(port_coords)
    except Exception as e:
        print(e)
        print(f'SORRY WRONG INPUT (THIS IS THE called DoEval file of {name_of_script})')


def FINAL_OUTPUT():
    return final_B
##########################################
if __name__ == "__main__":
    print(f'system args: {sys.argv}')
    print(f"name_of_script : {name_of_script}")
    if len(sys.argv) == 2:
         DoEval(sys.argv[1])
         fin = FINAL_OUTPUT()
         print(f"final output is {fin}")
    else: 
         print(f'SORRY! not correct args for {name_of_script}')
    
    # DoEval('A12TT')
    # FINAL_OUTPUT()

