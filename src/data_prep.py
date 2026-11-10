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
from config import (
    COMMUNITY_FLOODING,
    TAX_PARCELS,
    PREVIOUS_COMMUNITY_FLOODING,
    FLOOD_UNION,
)

NEW_FIELDS = [
    ("sq_ft", "DOUBLE", 0),
    ("fema_sfha", "TEXT", 1),
    ("community_flooding", "TEXT", 1),
    ("previous_community_flooding", "TEXT", 1),
    ("com_decrease", "TEXT", 1),
    ("com_increase", "TEXT", 1),
    ("com_no_change", "TEXT", 1),
    ("com_fema_overlap", "TEXT", 1),
]


def calc_square_footage(dataset):
    """
    Calculate the square footage of a polygon dataset.

    Parameters:
    dataset (str): Path to the polygon dataset for which to calculate square footage.
    """
    try:
        # Calculate square footage
        arcpy.CalculateField_management(dataset, "sq_ft", "!SHAPE.area!", "PYTHON3")

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
        arcpy.MakeFeatureLayer_management(fema_sfha, "fema_sfha_lyr")
        selected = arcpy.SelectLayerByAttribute_management(
            "fema_sfha_lyr", "NEW_SELECTION", "SFHA_TF = 'F'"
        )

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
        arcpy.MakeFeatureLayer_management(buildings, "buildings_lyr")
        selected = arcpy.SelectLayerByLocation_management(
            "buildings_lyr",
            "INTERSECT",
            county_boundary,
            invert_spatial_relationship="INVERT",
        )

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
                if field_type == "TEXT":
                    arcpy.AddField_management(
                        dataset, field_name, field_type, field_length=field_length
                    )
                else:
                    arcpy.AddField_management(dataset, field_name, field_type)

            # Calculate the field
            if field_name != "sq_ft":
                arcpy.CalculateField_management(dataset, field_name, "'F'", "PYTHON3")
            else:
                arcpy.CalculateField_management(dataset, field_name, "-9999", "PYTHON3")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)


def calculate_flooding_fields(
    dataset, fema_sfha, community_flooding, previous_community_flooding
):
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
        if arcpy.Exists("dataset_lyr"):
            arcpy.Delete_management("dataset_lyr")
        arcpy.MakeFeatureLayer_management(dataset, "dataset_lyr")

        # Select features that intersect with FEMA SFHA
        selected_fema = arcpy.SelectLayerByLocation_management(
            "dataset_lyr", "INTERSECT", fema_sfha, selection_type="NEW_SELECTION"
        )
        # Calculate fema sfa field
        arcpy.CalculateField_management(selected_fema, "fema_sfha", "'T'", "PYTHON3")

        # Select features that intersect with Community Flooding
        selected_community = arcpy.SelectLayerByLocation_management(
            "dataset_lyr",
            "INTERSECT",
            community_flooding,
            selection_type="NEW_SELECTION",
        )

        # Calculate community_flooding field
        arcpy.CalculateField_management(
            selected_community, "community_flooding", "'T'", "PYTHON3"
        )

        # Select features that intersect with Previous Community Flooding
        selected_community = arcpy.SelectLayerByLocation_management(
            "dataset_lyr",
            "INTERSECT",
            previous_community_flooding,
            selection_type="NEW_SELECTION",
        )

        # Calculate previous_community_flooding field
        arcpy.CalculateField_management(
            selected_community, "previous_community_flooding", "'T'", "PYTHON3"
        )

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)


def create_flood_union_dataset(old_flooding, new_flooding):
    """
    Create the flooding union dataset and populate the com_increase,
    com_decrease and com_no_change fields.

    Parameters:
    dataset (str): Path to the dataset for which to calculate flooding fields.
    old_flooding (str): Path to the old community flooding
    new_flooding (str): Path to the new community flooding
    """

    try:
        # Check if the output dataset already exists.  If so, delete it.
        if arcpy.Exists(dataset=FLOOD_UNION):
            arcpy.management.Delete(FLOOD_UNION)

        # Add a 'new' field to the new community flooding and calculate it to 'T'
        field_names = [field.name for field in arcpy.ListFields(new_flooding)]
        if "new" not in field_names:
            arcpy.AddField_management(
                in_table=new_flooding,
                field_name="new",
                field_type="TEXT",
                field_length=1,
            )
        arcpy.management.CalculateField(
            in_table=new_flooding,
            field="new",
            expression="'T'",
            expression_type="PYTHON3",
        )

        # Add a 'prev' field to the old community flooding and calculate it to 'T'
        field_names = [field.name for field in arcpy.ListFields(old_flooding)]
        if "prev" not in field_names:
            arcpy.AddField_management(
                in_table=old_flooding,
                field_name="prev",
                field_type="TEXT",
                field_length=1,
            )
        arcpy.management.CalculateField(
            in_table=old_flooding,
            field="prev",
            expression="'T'",
            expression_type="PYTHON3",
        )

        # Perform an intersection of the old and new flooding.
        arcpy.analysis.Union(
            in_features=[new_flooding, old_flooding],
            out_feature_class=FLOOD_UNION,
            join_attributes="ALL",
        )

        # In the output dataset, add these fields and calculate them to 'F': com_increase, com_decrease, com_no_change
        for field in ("com_increase", "com_decrease", "com_no_change"):
            arcpy.AddField_management(
                in_table=FLOOD_UNION,
                field_name=field,
                field_type="TEXT",
                field_length=1,
            )

            arcpy.management.CalculateField(
                in_table=FLOOD_UNION,
                field=field,
                expression="'F'",
                expression_type="PYTHON3",
            )

        # Select all rows where all the 'new' values are 'T' but inverse the selection.
        # Then, calculate these selected rows to 'F' for the 'new' column.
        selected_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=FLOOD_UNION,
            selection_type="NEW_SELECTION",
            where_clause="new = 'T'",
            invert_where_clause="INVERT",
        )
        arcpy.management.CalculateField(
            in_table=selected_rows,
            field="new",
            expression="'F'",
            expression_type="PYTHON3",
        )

        # Select all rows where all the 'prev' values are 'T' but inverse the selection.
        # Then, calculate these selected rows to 'F' for the 'prev' column.
        selected_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=FLOOD_UNION,
            selection_type="NEW_SELECTION",
            where_clause="prev = 'T'",
            invert_where_clause="INVERT",
        )
        arcpy.management.CalculateField(
            in_table=selected_rows,
            field="prev",
            expression="'F'",
            expression_type="PYTHON3",
        )

        # Calculate the fields based on the following selections:
        # If 'new' == 'T' and 'prev' == 'F', 'com_increase' = 'T'
        selected_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=FLOOD_UNION,
            selection_type="NEW_SELECTION",
            where_clause="new = 'T' and prev = 'F'",
        )
        arcpy.management.CalculateField(
            in_table=selected_rows,
            field="com_increase",
            expression="'T'",
            expression_type="PYTHON3",
        )

        # If 'new' == 'F' and 'prev' == 'T', 'com_decrease' = 'T'
        selected_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=FLOOD_UNION,
            selection_type="NEW_SELECTION",
            where_clause="new = 'F' and prev = 'T'",
        )
        arcpy.management.CalculateField(
            in_table=selected_rows,
            field="com_decrease",
            expression="'T'",
            expression_type="PYTHON3",
        )

        # If 'new' == 'T' and 'prev' == 'T', 'com_no_change' = 'T'
        selected_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=FLOOD_UNION,
            selection_type="NEW_SELECTION",
            where_clause="new = 'T' and prev = 'T'",
        )
        arcpy.management.CalculateField(
            in_table=selected_rows,
            field="com_no_change",
            expression="'T'",
            expression_type="PYTHON3",
        )

        # Drop unneeded fields
        keep_fields = [
            "OBJECTID",
            "Shape",
            "new",
            "prev",
            "Shape_Length",
            "Shape_Area",
            "com_increase",
            "com_decrease",
            "com_no_change",
        ]
        field_name_list = [field.name for field in arcpy.ListFields(FLOOD_UNION)]
        for field_name in field_name_list:
            if field_name not in keep_fields:
                arcpy.management.DeleteField(
                    in_table=FLOOD_UNION, drop_field=field_name
                )

    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        sys.exit(1)


def update_dataset_with_change_fields(dataset, union_flooding):
    """
    Update the parcel data using the union dataset and populate the com_increase,
    com_decrease and com_no_change fields.

    Parameters:
    dataset (str): Path to the dataset for which to calculate flooding fields.
    union_flooding (str): Path to the union dataset of the old and new flooding
    """
    # Initially calculate the fields to 'F'
    for field_name in ["com_increase", "com_decrease", "com_no_change"]:
        arcpy.management.CalculateField(
            in_table=dataset,
            field=field_name,
            expression="'F'",
            expression_type="PYTHON3",
        )

    # Select all the parcels that intersect the union flooding based on the
    # change fields and update the parcel attribution
    for field_name in ["com_increase", "com_decrease", "com_no_change"]:
        selected_union_rows = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=union_flooding,
            selection_type="NEW_SELECTION",
            where_clause=field_name + " = 'T'",
        )

        print(field_name, arcpy.management.GetCount(selected_union_rows)[0])

        selected_rows = arcpy.management.SelectLayerByLocation(
            in_layer=dataset,
            overlap_type="INTERSECT",
            select_features=selected_union_rows,
            selection_type="NEW_SELECTION",
        )

        print("Intersects:", arcpy.management.GetCount(selected_rows)[0])

        arcpy.management.CalculateField(
            in_table=selected_rows,
            field=field_name,
            expression="'T'",
            expression_type="PYTHON3",
        )


def main(
    buildings,
    fema_sfha,
    county_boundary,
    community_flooding,
    parcels,
    previous_community_flooding,
):
    """
    Main function to prepare the data for analysis.

    Parameters:
    buildings (str): Path to the buildings feature class.
    fema_sfha (str): Path to the FEMA SFHA feature class.
    county_boundary (str): Path to the county boundary feature class.
    community_flooding (str): Path to the Community Flooding feature class.
    parcels (str): Path to the tax parcels feature class.
    previous_community_flooding (str): Path the previous community flooding feature class
    """

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
        calculate_flooding_fields(
            dataset, fema_sfha, community_flooding, previous_community_flooding
        )

    # Create the Old/New Union flooding dataset
    print("Creating the union dataset of the flooding")
    create_flood_union_dataset(
        old_flooding=PREVIOUS_COMMUNITY_FLOODING, new_flooding=COMMUNITY_FLOODING
    )

    # Update the parcels and buildings with flooding change field data
    for dataset in [buildings, parcels]:
        print(f"Calculating the change fields for dataset: {dataset}")
        update_dataset_with_change_fields(dataset=dataset, union_flooding=FLOOD_UNION)


if __name__ == "__main__":
    main(
        buildings=BUILDINGS,
        fema_sfha=FEMA_FLOODING,
        county_boundary=COUNTY_BOUNDARY,
        community_flooding=COMMUNITY_FLOODING,
        previous_community_flooding=PREVIOUS_COMMUNITY_FLOODING,
        parcels=TAX_PARCELS,
    )
