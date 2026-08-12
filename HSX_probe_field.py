import pyvista as pv
import numpy as np
from moose import geometry
from flare import model
from flare.analysis import bfield
import argparse
import json

# Centralized list of supported configurations — easy to expand later
SUPPORTED_MODELS = ["qhs"]
DEFAULT_MODEL = "qhs"

#Command Line argument support 
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run probe configuration and analysis."
    )

    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"Model choice configuration (choices: {', '.join(SUPPORTED_MODELS)})",
    )

    parser.add_argument(
        "--probe-length",
        type=float,
        default=0.05,
        help="Probe length in meters (default: 0.05, must be >= 0)",
    )

    parser.add_argument(
        "--verbose",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Output additional information about ports",
    )

    parser.add_argument(
        "--interactive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the GUI interface",
    )

    args = parser.parse_args()

    if args.probe_length < 0:
        parser.error("--probe-length must be greater than or equal to 0.")

    return args

args = parse_arguments()
probe_length = args.probe_length
ModelChoice = args.model
verbose = args.verbose
InteractiveMode = args.interactive
print(f"Running with model: {args.model}")
    
# ModelChoice = 'hill_8'
# ModelComparison = True # make comparisons between models (model 1 and 2)

# VariableLength_ON = input("Would you like a variable length WISP probe (y/n)?")
# if VariableLength_ON == 'y':
#     while True:
#         try:
#             probe_length = float(input("What length of probe would you like for this test? : "))
#             break
#         except ValueError:
#             print("Input a integer or decimal value.")
# if VariableLength_ON == 'n':
#     print('Probe length set to default 0.05 m')
#     probe_length = 0.05

#if verbose: Do something or print messages

# Set up a list to temp. catch the point selections
# Click history centroids
ClickedCentroids = []



'''
bfield.eval() is in r,z,phi, and is also in radians !!!! just so you know...
'''



#pv.set_jupyter_backend('trame') # attempt to get this to run with GPU -- ignore
'''
            === HSX B-Field Evaluator for WISP Gauge ===
Version 3.0 

  Type the name of the HSX port that you would like to install the WISP gauge in. 
  The output wil tell you the magnetic feild at the tip of the guage.
  At the top of the code, you may choose "InteractiveMode = True," which will
  render a 3D interactive STL that you can rotote, selct a port, and have the field
  determined.
  Activate verbose mode for more data to be printed in the terminal. 

    Data is printed in the terminal.

    [Draft 3] (6/5/26)

    NOTES: 

    Originally written by Maxwell Loughan. Passed to Adam Rasmussen on August 3, 2026.

'''
def main():
    ########### LIST of PORTS ################
    with open("max_port_positions.json", "r") as f:
        port_dict = json.load(f)
    '''
    NOTES: 

    There is a centroid problem where one of the top ports (commented above) has a centrpoid that is actually NOT in the middle of the port 
    The actual centroid can (seemingly) be determined by clicking on the rim (however, the rim might be raised...)

    This is due to the the arrangement of the panels on the port opening. 
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
    #model.load("HSX/hill_8_config") # model 2
    if ModelChoice == 'qhs':
        model.load("HSX/qhs/mgrid") # model 1
    if ModelChoice == 'hill_8':
        model.load("HSX/hill_8_config") #model 2

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
        
        # Now we can compute the centroid of the flat region 

        # Extract the flat region
        flat_region_mesh = mesh.extract_cells(flat_cell_ids)

        # Compute the average positions of the cell centers 
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

        # B-field Evaluation at Centroid and Data Display
        bfield_eval = bfield.eval(region_centroid[0], region_centroid[1], region_centroid[2])
        print(f"\n--- Selection Registered ---")
        if verbose: 
            print(f"Clicked coordinate: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}]")
            print(f"Flat region includes {len(flat_cell_ids)} cells.")
            print(f"Port centroid coordinates: {region_centroid}")
            print(f"B-field at centroid of port opening (flat face): {bfield_eval}")
        
        # this is a temp. way to append the clicked centoids to the list to get port IDs
        ClickedCentroids.extend([region_centroid])

        # Index of the specific triangular centroid
        cell_index = mesh.find_closest_cell(region_centroid)
        
        # Normal vector array to the cell centroid
        raw_normal = mesh['Normals'][cell_index]
        
        # Invert the vector direction to point inward toward the internal volume
        inward_normal = raw_normal * -1
        if verbose: 
            print(f"Inward Face Normal (vector of WISP Gauge extension): [{inward_normal[0]:.4f}, {inward_normal[1]:.4f}, {inward_normal[2]:.4f}]")
        
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
        ProbeTip_coordinate_raw = ((region_centroid[0] + (probe_length * inward_normal[0])), 
                                   (region_centroid[1] + (probe_length * inward_normal[1])), 
                                   (region_centroid[2] + (probe_length * inward_normal[2])))
        ProbeTip_coordinate = [float(x) for x in ProbeTip_coordinate_raw]
        if verbose: 
            print(f"coordinate of probe tip: {ProbeTip_coordinate}")
        ProbeTip_B = bfield.eval((region_centroid[0] + (probe_length * inward_normal[0])), (region_centroid[1] + (probe_length * inward_normal[1])), (region_centroid[2] + (probe_length * inward_normal[2])))
        
        # if ProbeTip_B == '[0. 0. 0.]':
        #     if PrintZeros == True:
        #         print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")
        #     else:
        #         pass
        # else:
        #     print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")
        print(f"B-feild at WISP Gauge tip: {ProbeTip_B}")

        # Add arrow to plotter and track via container list index
        current_arrow[0] = plotter.add_mesh(arrow_mesh, color='red', label="Inward Normal Vector")

    # We will separate things out into quadrants to make selection easy
    # starting from the loaded front facing quandrant and moving CW

 

    ##### GUI window and selector ##### 
    if InteractiveMode:     
        plotter.enable_surface_point_picking(callback=my_callback, show_point=True)
        plotter.add_legend()
        plotter.show_axes()
        plotter.show()
        if verbose: 
            print('\nThe centroids of each port is: ',end="\n\n")
            print(ClickedCentroids)
    else:

    ########### In-Terminal User Interface (non-Visual) ################################
        def PortSelector(portnumber): # inut whould be of format : [x, y, z] (assuming cartisian coords)
            port_output = my_callback(portnumber)
            return port_output

        # Informational Launch Message
        print('''
                -----------------------------------------------
              - In-Terminal Port/Probe Magnetic Feild Evaluator -
                -----------------------------------------------
              
            INPUT:  Port ID 
            Output: Magnetic Feild at the tip of the WISP Gauge
            
            CONVENTIONS: 
                    HSX is separated into four quadrants (A,B,C, and D). 
                    In each of those quadrants are numerous 2-3/4" ports that may hold a gauge is unused.

                    According to the geometry of HSX the ports (of interest) are identified as:

                    Qij: Top (TT), Middle-Top (MT), Middle-Middle (MM), Middle-Bottom (MB), Bottom (BB) 

                    Where Q is the quadrant, and ij are the space inbetween the six primary coils (12, 23, 34, 45, and 56).

                    To identify, its "Port ID" is the Quadrant stiched tegether with spacing, and then location.
                    A valid Port ID would look like: 'A12MT' 

            ===> To end the program, type 'end'.
              
                    Quadrants are labeled by starting at a front facing quadrant, 
                    and then moving CCW around HSX. By altering the script, 
                    switching 'InteractiveMode' to 'True" will show you the front facing
                    'Quadrant 1.' This is placed at the top x axis of the STL file.

              PROBE: 
                    The length of the probe is in meters, assuming the STL file is to scale in meters.
                    Type 'length' to change the depth of the magnetif feild evaluation long the extension 
                    vector of the WISP gauge. Simply press ENTER to default to (0.05)

              AVAILABLE PORTS: 

                        Q12 : TT, MT, MM, MB
                        Q23 : TT, MT, MM, MB, BB
                        Q34 : MT
                        Q45 : NONE
                        Q56 : TT, MB, IN 
                    
                    PRIME POSITIONS:
                    
                        QP12 : BB, MB, MM, MT
                        QP23 : BB, MB, MM, MT, TT
                        QP34 : MB,
                        QP45 : NONE
                        QP56 : BB, MT, IN
        '''

        )

        with open("max_port_names.json", "r"):
            Port_Names = json.load(f)

        for i in Port_Names: # to do every prot for eval. 
            
            print(f" Port: {i}")
            chosen_port = i 
            try: 
                PortString = str(chosen_port)
                if PortString[1] == 'P':
                    quadrant_interval = PortString[0] + PortString[1] + PortString[2] + PortString[3]
                    if verbose: 
                        print(f'Quadrant_interval = {quadrant_interval}')
                    port_position = PortString[4] + PortString[5]
                    if verbose: 
                        print(f'Position = {port_position}')
                    port_coords = port_dict[quadrant_interval][port_position]
                    if verbose: 
                        print(f"Selected port coordinates: {port_coords}")
                    PortSelector(port_coords)
                else:

                    quadrant_interval = PortString[0] + PortString[1] + PortString[2] 
                    if verbose: 
                        print(f'Quadrant_interval = {quadrant_interval}')
                    port_position = PortString[3] + PortString[4]
                    if verbose: 
                        print(f'Position = {port_position}')
                    port_coords = port_dict[quadrant_interval][port_position]
                    if verbose: 
                        print(f"Selected port coordinates: {port_coords}")
                    PortSelector(port_coords)
            except Exception as e:
                if chosen_port == 'end':
                    pass
                else:
                    print(f'''
                    =============================================================================
                                    Invalid Input: '{e}'.
                    =============================================================================

                        ''')


        # while True: 
        #     chosen_port = input("What port would you like to evaluate? #: ")
        #     try: 
        #         PortString = str(chosen_port)
        #         if PortString[1] == 'P':
        #             quadrant_interval = PortString[0] + PortString[1] + PortString[2] + PortString[3]
        #             if verbose: print(f'Quadrant_interval = {quadrant_interval}')
        #             port_position = PortString[4] + PortString[5]
        #             if verbose: print(f'Position = {port_position}')
        #             port_coords = port_dict[quadrant_interval][port_position]
        #             if verbose: print(f"Selected port coordinates: {port_coords}")
        #             PortSelector(port_coords)
        #         else:

        #             quadrant_interval = PortString[0] + PortString[1] + PortString[2] 
        #             if verbose: print(f'Quadrant_interval = {quadrant_interval}')
        #             port_position = PortString[3] + PortString[4]
        #             if verbose: print(f'Position = {port_position}')
        #             port_coords = port_dict[quadrant_interval][port_position]
        #             if verbose: print(f"Selected port coordinates: {port_coords}")
        #             PortSelector(port_coords)
        #     except Exception as e:
        #         if chosen_port == 'end':
        #             pass
        #         elif chosen_port == 'show':
        #             Show_coords = port_coords
        #             pass 
        #         else:
        #             print(f'''
        #             =============================================================================
        #                             Invalid Input: '{e}'.
        #             =============================================================================
                                    
        #             ==> Please input port in the format: QijPP 

        #                     where 'Q' is a quadrant A-D, 
        #                     'ij' is a position between two coils (12, 23, 34, 45, 56)
        #                     and 'PP' is a position in that interval (TT, MT, MM, MB, BB, or IN).

        #                 If an interval does not have one of the positions listed above, 
        #                 it either does not exist, or is not approprate for selection.

        #             Type 'end' to exit program.
        #             ================================ TRY AGAIN ==================================

        #                 ''')
        #     if chosen_port == 'end':
        #         break
        #     if chosen_port == 'show':
        #         my_callback(Show_coords)
        #         plotter.show()
        #         Show_coords = [] #FIX THIS 
        

        print('============== Program Ended ==============')
    ###########################################

if __name__ == "__main__":
    main()

'''
TO DO: (6/11/26)
Fix the issue where you can only show the selected port with the "show" function once. you should be able to look indefinatly.
put in the other mgrid for hill_8_config file into the code so that the two fields can be compared at the probe tip (>10 deg).
'''
