"""
Script Name: data_within_flooding.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets within flooding areas.
"""
import sys
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS

QUERY_DICT = OrderedDict([
    ("Parcels within the FEMA SFHA", 0),
    ("Buildings within the FEMA SFHA", 0),
    ("Buildings within the FEMA SFHA > 600 square feet", 0),

    ("Parcels within the Community Floodplain", 0),
    ("Buildings within the Community Floodplain", 0),
    ("Buildings within the Community Floodplain > 600 square feet", 0),

    ("Parcels within the FEMA SFHA or within the Community Floodplain", 0),
    ("Buildings within the FEMA SFHA or within the Community Floodplain", 0),
    ("Buildings within the FEMA SFHA or within the Community Floodplain > 600 square feet", 0),

    ("Parcels that have both the FEMA SFHA and Community Floodplain", 0),
    ("Buildings that have both the FEMA SFHA and Community Floodplain", 0),
    ("Buildings that have both the FEMA SFHA and Community Floodplain > 600 square feet", 0)
])

def dataset_queries(dataset, prefix):
    """
    Perform queries related to dataset within flooding areas.

    Parameters:
    dataset (str): Path to the dataset feature class.
    prefix (str): Prefix for the query results. 
    """
    try:
        # dataset within the FEMA SFHA
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=dataset,
            selection_type="NEW_SELECTION",
            where_clause="fema_sfha = 'T'")

        QUERY_DICT[f"{prefix} within the FEMA SFHA"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # dataset within the Community Floodplain
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=dataset,
            selection_type="NEW_SELECTION",
            where_clause="community_flooding = 'T'")

        QUERY_DICT[f"{prefix} within the Community Floodplain"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # dataset within the FEMA SFHA and the Community Floodplain
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=dataset,
            selection_type="NEW_SELECTION",
            where_clause="fema_sfha = 'T' AND community_flooding = 'T'")

        QUERY_DICT[f"{prefix} that have both the FEMA SFHA and Community Floodplain"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        # dataset within the FEMA SFHA or the Community Floodplain
        selected = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=dataset,
            selection_type="NEW_SELECTION",
            where_clause="fema_sfha = 'T' OR community_flooding = 'T'")

        QUERY_DICT[f"{prefix} within the FEMA SFHA or within the Community Floodplain"] = \
            int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

        if prefix == "Buildings":
            # dataset within the FEMA SFHA > 600 square feet
            selected = arcpy.SelectLayerByAttribute_management(
                in_layer_or_view=dataset,
                selection_type="NEW_SELECTION",
                where_clause="fema_sfha = 'T' AND sq_ft > 600")

            QUERY_DICT[f"{prefix} within the FEMA SFHA > 600 square feet"] = \
                int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

            # dataset within the Community Floodplain > 600 square feet
            selected = arcpy.SelectLayerByAttribute_management(
                in_layer_or_view=dataset,
                selection_type="NEW_SELECTION",
                where_clause="community_flooding = 'T' AND sq_ft > 600")

            QUERY_DICT[f"{prefix} within the Community Floodplain > 600 square feet"] = \
                int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

            # dataset within the FEMA SFHA and the Community Floodplain > 600 square feet
            selected = arcpy.SelectLayerByAttribute_management(
                in_layer_or_view=dataset,
                selection_type="NEW_SELECTION",
                where_clause="fema_sfha = 'T' AND community_flooding = 'T' AND sq_ft > 600")

            QUERY_DICT[f"{prefix} that have both the FEMA SFHA and "
                       "Community Floodplain > 600 square feet"] = \
                int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

            # dataset within the FEMA SFHA or the Community Floodplain > 600 square feet
            selected = arcpy.SelectLayerByAttribute_management(
                in_layer_or_view=dataset,
                selection_type="NEW_SELECTION",
                where_clause="(fema_sfha = 'T' OR community_flooding = 'T') AND sq_ft > 600")

            QUERY_DICT[f"{prefix} within the FEMA SFHA or within the "
                       "Community Floodplain > 600 square feet"] = \
                int(arcpy.GetCount_management(in_rows=selected).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def main(parcels, buildings):
    """
    Main function to execute queries related to parcels in a county.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    """
    for dataset, prefix in [(parcels, "Parcels"), (buildings, "Buildings")]:
        dataset_queries(dataset, prefix)

    return QUERY_DICT

if __name__ == "__main__":
    result = main(
        parcels=TAX_PARCELS,
        buildings=BUILDINGS)

    for key, value in result.items():
        print(f"{key}: {value}")
