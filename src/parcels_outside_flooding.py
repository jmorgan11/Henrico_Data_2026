"""
Script Name: parcels_outside_fema_sfha.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to parcels outside of flooding areas.
"""
from collections import OrderedDict
import arcpy
from config import BUILDINGS, FEMA_FLOODING, TAX_PARCELS, COMMUNITY_FLOODING, FEMA_COMM_FLOODING

QUERY_DICT = OrderedDict([
    ("Parcels outside the FEMA SFHA", 0),
    ("Buildings outside the FEMA SFHA", 0),
    ("Buildings outside the FEMA SFHA > 600 square feet", 0),
    ("Parcels outside the Community Floodplain", 0),
    ("Buildings outside the Community Floodplain", 0),
    ("Buildings outside the Community Floodplain > 600 square feet", 0),
    ("Parcels outside the FEMA SFHA and the Community Floodplain", 0),
    ("Buildings outside the FEMA SFHA and the Community Floodplain", 0),
    ("Buildings outside the FEMA SFHA and the Community Floodplain > 600 square feet", 0)    
])

def main(parcels, fema_flooding, comm_flooding, fema_comm_flooding, buildings):
    """
    Main function to execute queries related to parcels in a county.

    Parameters:
    parcels (str): Path to the parcels feature class.
    fema_flooding (str): Path to the FEMA flooding feature class.
    comm_flooding (str): Path to the Community flooding feature class.
    buildings (str): Path to the buildings feature class.
    """
    for flooding in [fema_flooding, comm_flooding, fema_comm_flooding]:
        if flooding == fema_flooding:
            prefix = "FEMA SFHA"
        elif flooding == comm_flooding:
            prefix = "Community Floodplain"
        else:
            prefix = "FEMA SFHA and the Community Floodplain"

        # Parcels outside the flooding
        parcels_outside_flooding = arcpy.SelectLayerByLocation_management(
            parcels, "INTERSECT",
            flooding, selection_type="NEW_SELECTION",
            invert_spatial_relationship=True)

        QUERY_DICT[f"Parcels outside the {prefix}"] = \
            int(arcpy.GetCount_management(parcels_outside_flooding).getOutput(0))
      
        # Buildings outside the flooding
        buildings_outside_flooding = arcpy.SelectLayerByLocation_management(
            buildings, "INTERSECT",
            flooding, selection_type="NEW_SELECTION",
            invert_spatial_relationship=True)

        QUERY_DICT[f"Buildings outside the {prefix}"] = \
            int(arcpy.GetCount_management(buildings_outside_flooding).getOutput(0))

        # Buildings outside the flooding > 600 square feet
        large_buildings = arcpy.SelectLayerByAttribute_management(
            buildings_outside_flooding, "SUBSET_SELECTION", "sq_ft > 600")

        QUERY_DICT[f"Buildings outside the {prefix} > 600 square feet"] = \
            int(arcpy.GetCount_management(large_buildings).getOutput(0))

    return QUERY_DICT

if __name__ == "__main__":
    result = main(
        parcels=TAX_PARCELS, 
        fema_flooding=FEMA_FLOODING,
        comm_flooding=COMMUNITY_FLOODING,
        fema_comm_flooding=FEMA_COMM_FLOODING,
        buildings=BUILDINGS)  

    for key, value in result.items():
        print(f"{key}: {value}")
