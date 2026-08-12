'''
MAIN HSX file for comparing different configurations

    Loads both the 'mgrid' and 'hill_8' configuration files
    and produces magnetic field vectors at the WISP 'probe tip'
    for each port. The vector magnetic vector separation 
    between each of the configurations is compared for each 
    of the defined ports sequentially. 

We intend to check if the magnetic vector separation is less than 10 degrees for each port/config.
Spoiler alert -- all under 10 deg. 

-Maxwell Loughan
'''
verbose = True

import subprocess
import re
import numpy as np

# Maybe make this a big loop to have a constant selection? 
# maybe go through all the ports to determine the angular separation under 10 deg? 
# go back to the HSX_probe_field file to see if you can print out the b-field for all the ports (to make sure there are no 0.0.0 feilds)?
# 6/15/26
'''
Ports with defioned feild vectors: (true for both files)

A12TT
A12MT
A12MM
A12MB
A23TT
A23MT
A23MM
A23MB
A23BB
AP12BB
AP12MB
AP12MM
AP12MT 

'''
PortEvalList = [
    'A12TT',
    'A12MT',
    'A12MM',
    'A12MB',
    'A23TT',
    'A23MT',
    'A23MM',
    'A23MB',
    'A23BB',
    'AP12BB',
    'AP12MB',
    'AP12MM',
    'AP12MT' 
]
port_of_choice = "A12TT"

MultiPortEval = True 


# Angular Separation of Vectors
def Angular_Vector_Separation(A_vector, B_vector, rad=False, VerboseMode=False):
    # Returns (smallest) angle between A and B in deg
    # -- can switch to rad is needed
    A = np.array(A_vector)
    B = np.array(B_vector)

    # Calculate dot product and magnitudes
    dot_product = np.dot(A, B)
    magnitude_A = np.linalg.norm(A)
    magnitude_B = np.linalg.norm(B)

    # Calculate the angle
    angle_radians = np.arccos(dot_product / (magnitude_A * magnitude_B))
    angle_degrees = np.degrees(angle_radians)

    if VerboseMode == True: 
        print(f"Angle between A and B: {angle_degrees} degrees")

    if rad == True : 
        return angle_radians
    else:
        return angle_degrees

if MultiPortEval == True: 
    for port in PortEvalList:
            
        code1 = subprocess.run(["python", "Mgrid_Config_import.py", port], capture_output=True, text=True)
        code2 = subprocess.run(["python", "Hill_8_Config_import.py", port], capture_output=True, text=True)

        # print(code1.stdout)
        # print(code2.stdout)

        # Scraping the output of the mgrid file
        match1 = re.search(r"B feild : \s*(.*)", code1.stdout)
        program_name1 = re.search(r"name_of_script : \s*(.*)", code1.stdout)
        if program_name1:
            if verbose == True: print(f"program name: {program_name1.group(1).strip()}")
        if match1:
            coords1 = match1.group(1).strip()
            # print(f"{coords1}")

        #scraping the output of the hill_8 file 
        match2 = re.search(r"B feild : \s*(.*)", code2.stdout)
        program_name2 = re.search(r"name_of_script : \s*(.*)", code2.stdout)
        if program_name2:
            if verbose == True: print(f"program name: {program_name2.group(1).strip()}")
        if match2:
            coords2 = match2.group(1).strip()
            # print(f"{coords2}")

        ####### B-Field Coordinates from .mgrid file ######
        coords1_cleaned = coords1.strip('[]')

        elements1 = coords1_cleaned.split()

        try:
            B_vector_1 = [float(element) for element in elements1]
        except ValueError:
            # Handle cases where conversion is not possible, for safety
            B_vector_1 = [element for element in elements1]

        if verbose == True: print(f'B vector 1: {B_vector_1}')
        ####################################################

        ####### B-Field Coordinates from hill_8_cofig file ######
        coords2_cleaned = coords2.strip('[]')

        elements2 = coords2_cleaned.split()

        try:
            B_vector_2 = [float(element) for element in elements2]
        except ValueError:
            # Handle cases where conversion is not possible, for safety
            B_vector_2 = [element for element in elements2]

        if verbose == True: print(f'B vector 2: {B_vector_2}')
        ####################################################

        Bfeild_separation_deg = Angular_Vector_Separation(B_vector_1, B_vector_2)
        print(f"B Field Separation at {port} in Deg : {Bfeild_separation_deg} deg")
else:

    code1 = subprocess.run(["python", "Mgrid_Config_import.py", port_of_choice], capture_output=True, text=True)
    code2 = subprocess.run(["python", "Hill_8_Config_import.py", port_of_choice], capture_output=True, text=True)

    # print(code1.stdout)
    # print(code2.stdout)

    # Scraping the output of the mgrid file
    match1 = re.search(r"B feild : \s*(.*)", code1.stdout)
    program_name1 = re.search(r"name_of_script : \s*(.*)", code1.stdout)
    if program_name1:
        if verbose == True: print(f"program name: {program_name1.group(1).strip()}")
    if match1:
        coords1 = match1.group(1).strip()
        # print(f"{coords1}")

    #scraping the output of the hill_8 file 
    match2 = re.search(r"B feild : \s*(.*)", code2.stdout)
    program_name2 = re.search(r"name_of_script : \s*(.*)", code2.stdout)
    if program_name2:
        if verbose == True: print(f"program name: {program_name2.group(1).strip()}")
    if match2:
        coords2 = match2.group(1).strip()
        # print(f"{coords2}")

    ####### B-Field Coordinates from .mgrid file ######
    coords1_cleaned = coords1.strip('[]')

    elements1 = coords1_cleaned.split()

    try:
        B_vector_1 = [float(element) for element in elements1]
    except ValueError:
        # Handle cases where conversion is not possible, for safety
        B_vector_1 = [element for element in elements1]

    if verbose == True: print(f'B vector 1: {B_vector_1}')
    ####################################################

    ####### B-Field Coordinates from hill_8_cofig file ######
    coords2_cleaned = coords2.strip('[]')

    elements2 = coords2_cleaned.split()

    try:
        B_vector_2 = [float(element) for element in elements2]
    except ValueError:
        # Handle cases where conversion is not possible, for safety
        B_vector_2 = [element for element in elements2]

    if verbose == True: print(f'B vector 2: {B_vector_2}')
    ####################################################

    # # Angular Separation of Vectors
    # def Angular_Vector_Separation(A_vector, B_vector, rad=False, VerboseMode=False):
    #     # Returns (smallest) angle between A and B in deg
    #     # -- can switch to rad is needed
    #     A = np.array(A_vector)
    #     B = np.array(B_vector)

    #     # Calculate dot product and magnitudes
    #     dot_product = np.dot(A, B)
    #     magnitude_A = np.linalg.norm(A)
    #     magnitude_B = np.linalg.norm(B)

    #     # Calculate the angle
    #     angle_radians = np.arccos(dot_product / (magnitude_A * magnitude_B))
    #     angle_degrees = np.degrees(angle_radians)

    #     if VerboseMode == True: 
    #         print(f"Angle between A and B: {angle_degrees} degrees")

    #     if rad == True : 
    #         return angle_radians
    #     else:
    #         return angle_degrees

    Bfeild_separation_deg = Angular_Vector_Separation(B_vector_1, B_vector_2)
    print(f"B Field Separation at {port_of_choice} in Deg : {Bfeild_separation_deg} deg")


'''
OUTPUT FOR DEFINED PORTS: 
B Field Separation at A12TT in Deg : 0.2911193757717471 deg
B Field Separation at A12MT in Deg : 0.21520068246504045 deg
B Field Separation at A12MM in Deg : 0.27071604131326454 deg
B Field Separation at A12MB in Deg : 0.256951005496879 deg
B Field Separation at A23TT in Deg : 0.6452343164217009 deg
B Field Separation at A23MT in Deg : 0.33310058114182933 deg
B Field Separation at A23MM in Deg : 0.4280880882503671 deg
B Field Separation at A23MB in Deg : 0.6755126483553964 deg
B Field Separation at A23BB in Deg : 4.688697036095408 deg
B Field Separation at AP12BB in Deg : 0.2911193757717471 deg
B Field Separation at AP12MB in Deg : 0.21520068246504045 deg
B Field Separation at AP12MM in Deg : 0.27071604131326454 deg
B Field Separation at AP12MT in Deg : 0.256951005496879 deg
'''