"""
Script Name: overlap_come_fema.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets 
             where the community flooding and the FEMA
             flooding overlap.
"""
import sys
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS


QUERY_DICT = OrderedDict([
    ("Parcels that have Community Floodplain but are "
    "already in FEMA SFHA (Potential No Change)", 0),
    ("Buildings  in Community Floodplain but are already "
    "in FEMA SFHA (Potential No Change)", 0),
    ("Buildings  in Community Floodplain but are already "
    "in FEMA SFHA (Potential No Change) > 600 square feet", 0)
])

def main(parcels, buildings, magistrate=None):
    """
    Main function to execute queries related to datasets where 
    the community flooding and the FEMA flooding overlap.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    """
    try:
        where_clause = "com_fema_overlap = 'T'"

        if magistrate:
            where_clause += f" And magistrate = '{magistrate}'"

        # Parcels with overlapping community and FEMA flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=parcels,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Parcels that have Community Floodplain but are " \
        "already in FEMA SFHA (Potential No Change)"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with overlapping community and FEMA flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Buildings  in Community Floodplain but are " \
        "already in FEMA SFHA (Potential No Change)"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with overlapping community and FEMA flooding and > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause + " And sq_ft >= 600")

        QUERY_DICT["Buildings  in Community Floodplain but are already in " \
        "FEMA SFHA (Potential No Change) > 600 square feet"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

    return QUERY_DICT

if __name__ == '__main__':
    result = main(parcels=TAX_PARCELS, buildings=BUILDINGS, magistrate=None)

    for key, value in result.items():
        print(f"{key}: {value}")
