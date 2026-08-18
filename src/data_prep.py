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
from config import BUILDINGS, FEMA_FLOODING, COUNTY_BOUNDARY
from config import COMMUNITY_FLOODING, TAX_PARCELS, PREVIOUS_COMMUNITY_FLOODING

NEW_FIELDS = [
    ('sq_ft', 'DOUBLE', 0),
    ('fema_sfha', 'TEXT', 1),
    ('community_flooding', 'TEXT', 1),
    ('previous_community_flooding', 'TEXT', 1)
]

def calc_square_footage(dataset):
    """
    Calculate the square footage of a polygon dataset.

    Parameters:
    dataset (str): Path to the polygon dataset for which to calculate square footage.
    """
    try:
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

def add_fields(dataset, fields):
    """
    Add fields to a dataset.

    Parameters:
    dataset (str): Path to the dataset to which fields will be added.
    fields (list): List of tuples containing field names and types.
    """
    try:
        for field_name, field_type, field_length in fields:
            if field_name not in [f.name for f in arcpy.ListFields(dataset)]:
                if field_type == 'TEXT':
                    arcpy.AddField_management(dataset,
                                              field_name,
                                              field_type,
                                              field_length=field_length)
                else:
                    arcpy.AddField_management(dataset, field_name, field_type)

            # Calculate the field
            if field_name != 'sq_ft':
                arcpy.CalculateField_management(dataset, field_name, "'F'", 'PYTHON3')
            else:
                arcpy.CalculateField_management(dataset, field_name, "-9999", 'PYTHON3')

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def calculate_flooding_fields(dataset, fema_sfha, community_flooding, previous_community_flooding):
    """
    Calculate the FEMA and Community Flooding fields for a dataset.

    Parameters:
    dataset (str): Path to the dataset for which to calculate flooding fields.
    fema_sfha (str): Path to the FEMA SFHA feature class.
    community_flooding (str): Path to the Community Flooding feature class. 
    previous_community_flooding (str): Path the previous Community Flooding feature class.
    """
    try:
        # Remove the dataset layer if it already exists
        if arcpy.Exists('dataset_lyr'):
            arcpy.Delete_management('dataset_lyr')
        arcpy.MakeFeatureLayer_management(dataset, 'dataset_lyr')

        # Select features that intersect with FEMA SFHA
        selected_fema = arcpy.SelectLayerByLocation_management(
            'dataset_lyr', 
            "INTERSECT", 
            fema_sfha,
            selection_type="NEW_SELECTION"
        )
        # Calculate fema sfa field
        arcpy.CalculateField_management(selected_fema, 'fema_sfha', "'T'", 'PYTHON3')

        # Select features that intersect with Community Flooding
        selected_community = arcpy.SelectLayerByLocation_management(
            'dataset_lyr', 
            "INTERSECT",    
            community_flooding,
            selection_type="NEW_SELECTION"
        )

        # Calculate community_flooding field
        arcpy.CalculateField_management(selected_community, 'community_flooding', "'T'", 'PYTHON3')

        # Select features that intersect with Previous Community Flooding
        selected_community = arcpy.SelectLayerByLocation_management(
            'dataset_lyr', 
            "INTERSECT",    
            previous_community_flooding,
            selection_type="NEW_SELECTION"
        )

        # Calculate previous_community_flooding field
        arcpy.CalculateField_management(selected_community,
                                        'previous_community_flooding', 
                                        "'T'", 'PYTHON3')

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)

def main(buildings, fema_sfha, county_boundary, community_flooding,
         parcels, previous_community_flooding):
    """
    Main function to prepare the data for analysis.

    Parameters:
    buildings (str): Path to the buildings feature class.
    fema_sfha (str): Path to the FEMA SFHA feature class.
    county_boundary (str): Path to the county boundary feature class.
    community_flooding (str): Path to the Community Flooding feature class.
    parcels (str): Path to the tax parcels feature class.    
    previous_community_flooding (str): Path the previous community flooding feature class"""

    # Add fields to the buildings and parcels datasets
    for dataset in [buildings, parcels]:
        print(f"Adding fields to dataset: {dataset}")
        add_fields(dataset, NEW_FIELDS)

    # Calculate square footage for the buildings dataset
    print(f"Calculating square footage for buildings dataset: {buildings}")
    calc_square_footage(buildings)

    # Remove non-FEMA SFHA flood polygons
    print("Removing non-FEMA SFHA flood polygons")
    remove_non_sfha_flooding(fema_sfha)

    # Remove buildings outside the county boundary
    print("Removing buildings outside the county boundary")
    remove_buildings_outside_county(buildings, county_boundary)

    # Calculate FEMA and Community Flooding fields for the buildings and parcels datasets
    for dataset in [buildings, parcels]:
        print(f"Calculating FEMA and Community Flooding fields for dataset: {dataset}")
        calculate_flooding_fields(dataset, fema_sfha,
                                  community_flooding,
                                  previous_community_flooding)

if __name__ == "__main__":
    main(
        buildings=BUILDINGS,
        fema_sfha=FEMA_FLOODING,
        county_boundary=COUNTY_BOUNDARY,
        community_flooding=COMMUNITY_FLOODING,
        previous_community_flooding=PREVIOUS_COMMUNITY_FLOODING,
        parcels=TAX_PARCELS)
