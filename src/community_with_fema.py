"""
Script Name: community_with_fema.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets that have community flooding and FEMA flooding.
"""
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS
import sys

QUERY_DICT = OrderedDict([
    ("Parcels that have Community Floodplain but are already in FEMA SFHA (Potential No Change)", 0),
    ("Buildings  in Community Floodplain but are already in FEMA SFHA (Potential No Change)", 0),
    ("Buildings  in Community Floodplain but are already in FEMA SFHA (Potential No Change) > 600 square feet", 0)
])


def main(parcels, buildings):
    """
    Main function to execute queries related to datasets that have community flooding and FEMA flooding.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    """
    try:
        # Parcels that have Community Floodplain but are already in FEMA SFHA (Potential No Change)
        selected = arcpy.SelectLayerByAttribute_management(parcels, "NEW_SELECTION", "community_flooding = 'T' And fema_sfha = 'T'")
        QUERY_DICT["Parcels that have Community Floodplain but are already in FEMA SFHA (Potential No Change)"] = int(arcpy.GetCount_management(selected).getOutput(0))

        # Buildings  in Community Floodplain but are already in FEMA SFHA (Potential No Change)
        selected = arcpy.SelectLayerByAttribute_management(buildings, "NEW_SELECTION", "community_flooding = 'T' And fema_sfha = 'T'")
        QUERY_DICT["Buildings  in Community Floodplain but are already in FEMA SFHA (Potential No Change)"] = int(arcpy.GetCount_management(selected).getOutput(0))

        # Buildings with increasing community flooding and > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(buildings, "NEW_SELECTION", "community_flooding = 'T' And fema_sfha = 'T' And sq_ft >= 600")
        QUERY_DICT["Buildings  in Community Floodplain but are already in FEMA SFHA (Potential No Change) > 600 square feet"] = int(arcpy.GetCount_management(selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)        

    return QUERY_DICT

if __name__ == "__main__":
    result = main(
        parcels=TAX_PARCELS,
        buildings=BUILDINGS)

    for key, value in result.items():
        print(f"{key}: {value}")
