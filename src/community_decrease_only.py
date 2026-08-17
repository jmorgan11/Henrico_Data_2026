"""
Script Name: community_decrease_only.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets where the community flooding increased
"""
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS
import sys

QUERY_DICT = OrderedDict([
    ("Parcels who's only new condition is decreasing Community Floodplain (Decrease Only)", 0),
    ("Buildings who's only new condition is decreasing Community Floodplain (Decrease Only)", 0),
    ("Buildings who's only new condition is decreasing Community Floodplain (Decrease Only) > 600 square feet", 0)
])

def main(parcels, buildings):
    """
    Main function to execute queries related to datasets with increasing community flooding.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    """
    try:
        # Parcels with increasing community flooding
        selected = arcpy.SelectLayerByAttribute_management(parcels, "NEW_SELECTION", "community_flooding = 'F' And previous_community_flooding = 'T'")
        QUERY_DICT["Parcels who's only new condition is decreasing Community Floodplain (Decrease Only)"] = int(arcpy.GetCount_management(selected).getOutput(0))

        # Buildings with increasing community flooding
        selected = arcpy.SelectLayerByAttribute_management(buildings, "NEW_SELECTION", "community_flooding = 'F' And previous_community_flooding = 'T'")
        QUERY_DICT["Buildings who's only new condition is decreasing Community Floodplain (Decrease Only)"] = int(arcpy.GetCount_management(selected).getOutput(0))

        # Buildings with increasing community flooding and > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(buildings, "NEW_SELECTION", "community_flooding = 'F' And previous_community_flooding = 'T' And sq_ft >= 600")
        QUERY_DICT["Buildings who's only new condition is decreasing Community Floodplain (Decrease Only) > 600 square feet"] = int(arcpy.GetCount_management(selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)        

    return QUERY_DICT

if __name__ == '__main__':
    result = main(parcels=TAX_PARCELS, buildings=BUILDINGS)

    for key, value in result.items():
        print(f"{key}: {value}")     