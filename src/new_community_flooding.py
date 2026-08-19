"""
Script Name: new_community_flooding.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets where a community
             has new community flooding.
"""
import sys
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS

QUERY_DICT = OrderedDict([
    ("Parcels that had no Community Floodplains that are "
    "newly mapped into the Community Floodplains", 0),
    ("Buildings that had no Community Floodplains "
    "that are newly mapped into the Community Floodplain", 0),
    ("Buildings that had no Community Floodplains "
    "that are newly mapped into the Community Floodplains > 600 square feet", 0)
])

def main(parcels, buildings, magistrate=None):
    """
    Main function to execute queries related to datasets with new community flooding.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    magistrate (str: Optional): The magistrate name to query on.
    """
    try:
        where_clause = "community_flooding = 'T' And previous_community_flooding = 'F'"

        if magistrate:
            where_clause += f" And magistrate = '{magistrate}'"

        # Parcels with increasing community flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=parcels,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Parcels that had no Community Floodplains " \
        "that are newly mapped into the Community Floodplains"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with increasing community flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Buildings that had no Community Floodplains " \
        "that are newly mapped into the Community Floodplain"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with increasing community flooding and > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause + " And sq_ft >= 600")

        QUERY_DICT["Buildings that had no Community Floodplains that are " \
        "newly mapped into the Community Floodplains > 600 square feet"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

    return QUERY_DICT

if __name__ == '__main__':
    result = main(parcels=TAX_PARCELS, buildings=BUILDINGS, magistrate=None)

    for key, value in result.items():
        print(f"{key}: {value}")
