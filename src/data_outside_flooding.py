"""
Script Name: data_outside_flooding.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to datasets outside of flooding areas.
"""
from collections import OrderedDict
import arcpy
from config import BUILDINGS, TAX_PARCELS

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

def dataset_queries(dataset, prefix):
    """
    Perform queries related to dataset outside of flooding areas.

    Parameters:
    dataset (str): Path to the dataset feature class.
    prefix (str): Prefix for the query results. 
    """
    # dataset outside the FEMA SFHA
    selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "fema_sfha = 'F'")

    QUERY_DICT[f"{prefix} outside the FEMA SFHA"] = \
        int(arcpy.GetCount_management(selected).getOutput(0))

    # dataset outside the Community Floodplain
    selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "community_flooding = 'F'")

    QUERY_DICT[f"{prefix} outside the Community Floodplain"] = \
        int(arcpy.GetCount_management(selected).getOutput(0))

    # dataset outside the FEMA SFHA and the Community Floodplain
    selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "fema_sfha = 'F' AND community_flooding = 'F'")

    QUERY_DICT[f"{prefix} outside the FEMA SFHA and the Community Floodplain"] = \
        int(arcpy.GetCount_management(selected).getOutput(0))

    if prefix == "Buildings":
        # dataset outside the FEMA SFHA > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "fema_sfha = 'F' AND sq_ft > 600") 

        QUERY_DICT[f"{prefix} outside the FEMA SFHA > 600 square feet"] = \
            int(arcpy.GetCount_management(selected).getOutput(0))

        # dataset outside the Community Floodplain > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "community_flooding = 'F' AND sq_ft > 600")

        QUERY_DICT[f"{prefix} outside the Community Floodplain > 600 square feet"] = \
            int(arcpy.GetCount_management(selected).getOutput(0))
        
        # dataset outside the FEMA SFHA and the Community Floodplain > 600 square feet
        selected = arcpy.SelectLayerByAttribute_management(dataset, "NEW_SELECTION", "fema_sfha = 'F' AND community_flooding = 'F' AND sq_ft > 600")

        QUERY_DICT[f"{prefix} outside the FEMA SFHA and the Community Floodplain > 600 square feet"] = \
            int(arcpy.GetCount_management(selected).getOutput(0))
    

def main(parcels, buildings):
    """
    Main function to execute queries related to parcels in a county.

    Parameters:
    parcels (str): Path to the parcels feature class.
    buildings (str): Path to the buildings feature class.
    """
    for dataset, prefix in [(parcels, "Parcels"), (buildings, "Buildings")]:
        print(f"Performing queries for {prefix} dataset")
        dataset_queries(dataset, prefix)

    return QUERY_DICT

if __name__ == "__main__":
    result = main(
        parcels=TAX_PARCELS,
        buildings=BUILDINGS)

    for key, value in result.items():
        print(f"{key}: {value}")
