"""
Script Name: parcels_in_county.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains queries related to parcels within a specific county.
"""
import sys
from collections import OrderedDict
import arcpy
from config import BUILDINGS, COUNTY_BOUNDARY, TAX_PARCELS

QUERY_DICT = OrderedDict([
    ("Parcels in the county", 0),
    ("Buildings within the Parcels", 0),
    ("Buildings with the Parcels > 600 square feet", 0)
])

def main(parcels, county, buildings):
    """
    Main function to execute queries related to parcels in a county.

    Parameters:
    parcels (str): Path to the parcels feature class.
    county (str): Name of the county to filter parcels.
    buildings (str): Path to the buildings feature class.
    """
    try:
        # Parcels in the county
        parcel_intersect = arcpy.SelectLayerByLocation_management(
            parcels, "INTERSECT", county)

        QUERY_DICT["Parcels in the county"] = \
            int(arcpy.GetCount_management(parcel_intersect).getOutput(0))

        # Buildings within the Parcels
        building_intersect = arcpy.SelectLayerByLocation_management(
            buildings, "INTERSECT", parcel_intersect)

        QUERY_DICT["Buildings within the Parcels"] = \
            int(arcpy.GetCount_management(building_intersect).getOutput(0))

        # Buildings within the Parcels > 600 square feet
        large_buildings = arcpy.SelectLayerByAttribute_management(
            building_intersect, "SUBSET_SELECTION", "sq_ft > 600")

        QUERY_DICT["Buildings with the Parcels > 600 square feet"] = \
            int(arcpy.GetCount_management(large_buildings).getOutput(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

    return QUERY_DICT

if __name__ == "__main__":
    result = main(parcels=TAX_PARCELS, county=COUNTY_BOUNDARY, buildings=BUILDINGS)
    for query, count in result.items():
        print(f"\t{query}: {count:,}")
