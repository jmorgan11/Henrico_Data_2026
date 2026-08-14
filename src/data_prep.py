"""
SCRIPT NAME: data_prep.py
AUTHOR: Jesse Morgan
DATE: 2024-06-19
Description: This script prepares the data for analysis by performing necessary preprocessing steps, 
             such as cleaning, transforming, and organizing the data into a suitable 
             format for querying and analysis.
"""
import sys
import arcpy
from config import BUILDINGS, FEMA_FLOODING, COUNTY_BOUNDARY, COMMUNITY_FLOODING, FEMA_COMM_FLOODING

def calc_square_footage(dataset):
    """
    Calculate the square footage of a polygon dataset.

    Parameters:
    dataset (str): Path to the polygon dataset for which to calculate square footage.
    """
    try:
        # Add a new field for square footage if it doesn't exist
        if 'sq_ft' not in [f.name for f in arcpy.ListFields(dataset)]:
            arcpy.AddField_management(dataset, 'sq_ft', 'DOUBLE')

        # Calculate square footage
        arcpy.CalculateField_management(dataset, 'sq_ft', '!SHAPE.area!', 'PYTHON3')

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def remove_non_sfha_flooding(fema_sfha):
    """
    Remove flood polygons that are not FEMA SFHA.

    Parameters:
    fema_sfha (str): Path to the FEMA SFHA feature class.
    """
    try:
        # Select parcels that intersect with FEMA SFHA
        arcpy.MakeFeatureLayer_management(fema_sfha, 'fema_sfha_lyr')
        selected = arcpy.SelectLayerByAttribute_management(
            'fema_sfha_lyr', 
            'NEW_SELECTION', 
            "SFHA_TF = 'F'")

        # Delete selected parcels that do not intersect with FEMA SFHA
        arcpy.DeleteFeatures_management(selected)

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def remove_buildings_outside_county(buildings, county_boundary):
    """
    Remove buildings that are outside the county boundary.

    Parameters:
    buildings (str): Path to the buildings feature class.
    county_boundary (str): Path to the county boundary feature class.
    """
    try:
        # Select buildings that do not intersect with the county boundary
        arcpy.MakeFeatureLayer_management(buildings, 'buildings_lyr')
        selected = arcpy.SelectLayerByLocation_management(
            'buildings_lyr', 
            'INTERSECT', 
            county_boundary,
            invert_spatial_relationship="INVERT")

        # Delete selected buildings that do not intersect with the county boundary
        arcpy.DeleteFeatures_management(selected)

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def merge_flooding_datasets(fema_sfha, community_flooding, out_flooding):
    """
    Merge FEMA SFHA and Community Flooding datasets into a single dataset.

    Parameters:
    fema_sfha (str): Path to the FEMA SFHA feature class.
    community_flooding (str): Path to the Community Flooding feature class.
    out_flooding (str): Path to the output merged feature class.
    """
    try:
        # Delete the output dataset if it already exists
        if arcpy.Exists(out_flooding):
            arcpy.Delete_management(out_flooding)

        # Merge the two flooding datasets
        arcpy.Merge_management([fema_sfha, community_flooding], out_flooding)

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)


def main(buildings, fema_sfha, county_boundary, community_flooding, out_flooding):
    """
    Main function to prepare the data for analysis.

    Parameters:
    buildings (str): Path to the buildings feature class.
    fema_sfha (str): Path to the FEMA SFHA feature class.
    county_boundary (str): Path to the county boundary feature class.
    community_flooding (str): Path to the Community Flooding feature class.
    out_flooding (str): Path to the output merged flooding feature class.
    """
    # Calculate square footage for the buildings dataset
    print(f"Calculating square footage for buildings dataset: {buildings}")
    calc_square_footage(buildings)

    # Remove non-FEMA SFHA flood polygons
    print("Removing non-FEMA SFHA flood polygons")
    remove_non_sfha_flooding(fema_sfha)

    # Merge FEMA SFHA and Community Flooding datasets
    print("Merging FEMA SFHA and Community Flooding datasets")
    merge_flooding_datasets(fema_sfha, community_flooding, out_flooding=out_flooding)

    # Remove buildings outside the county boundary
    print("Removing buildings outside the county boundary")
    remove_buildings_outside_county(buildings, county_boundary)

if __name__ == "__main__":
    main(
        buildings=BUILDINGS,
        fema_sfha=FEMA_FLOODING,
        county_boundary=COUNTY_BOUNDARY,
        community_flooding=COMMUNITY_FLOODING,
        out_flooding=FEMA_COMM_FLOODING)
