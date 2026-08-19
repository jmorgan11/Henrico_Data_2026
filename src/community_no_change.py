"""
Script Name: new_community_increase.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets 
             where the community flooding no change. The communities
             may also include decrease in flooding and increase
             in flooding values.
"""
import sys
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS


QUERY_DICT = OrderedDict([
    ("Parcels within Community Floodplains but no change is occurring", 0),
    ("Buildings within Community Floodplains but no change is occurring", 0),
    ("Buildings within Community Floodplains but no change is occurring > 600 square feet", 0)
])

def main(parcels, buildings, magistrate=None):
    """
    Main function to execute queries related to datasets with no change in community flooding.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    magistrate (str: Optional): The magistrate name to query on.
    """
    try:
        where_clause = "com_no_change = 'T'"

        if magistrate:
            where_clause += f" And magistrate = '{magistrate}'"

        # Parcels with no change in community flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=parcels,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Parcels within Community Floodplains but no change is occurring"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with no change in community flooding
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause)

        QUERY_DICT["Buildings within Community Floodplains but no change is occurring"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # Buildings with no change community flooding and > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=buildings,
            selection_type="NEW_SELECTION",
            where_clause=where_clause + " And sq_ft >= 600")

        QUERY_DICT["Buildings within Community Floodplains but no change "
        "is occurring > 600 square feet"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

    return QUERY_DICT

if __name__ == '__main__':
    result = main(parcels=TAX_PARCELS, buildings=BUILDINGS, magistrate=None)

    for key, value in result.items():
        print(f"{key}: {value}")
