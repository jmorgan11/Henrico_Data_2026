"""
SCRIPT NAME: export_floodplain_address_list.py
AUTHOR: Jesse Morgan
DATE: 2026-11-23
Description: This script exports four Excel files of addresses.
    1. Parcels that have FEMA SFHA flooding.
    2. Parcels that have Community Floodplains.
    3. Buildings identified as Condas that intersect the FEMA SFHA flooding.
    4. Buildings identified as Condas that intersect the Community Floodplains.
"""

import arcpy
import os
from pathlib import Path
import pandas as pd
from config import OUT_PATH
from config import TAX_PARCELS
from config import BUILDINGS
from config import MASTER_ADDRESS_POINTS
from config import TAX_PARCELS_GPIN
from config import REPETITIVE_LOSS_AREAS

OUTPUT_FOLDER = os.path.join(OUT_PATH, "Floodplain_Address_Lists")

# Output Excel files
FEMA_SFHA_CONDOS = os.path.join(OUTPUT_FOLDER, "FEMA_SFHA_Condos_Addresses.xlsx")
COMMUNITY_CONDOS = os.path.join(OUTPUT_FOLDER, "Community_Floodplain_Condos_Addresses.xlsx")
FEMA_SFHA_PARCELS = os.path.join(OUTPUT_FOLDER, "FEMA_SFHA_Parcel_Addresses.xlsx")
COMMUNITY_PARCELS = os.path.join(OUTPUT_FOLDER, "Community_Parcel_Addresses.xlsx")
RLA_PARCELS = os.path.join(OUTPUT_FOLDER, "Repetitive_Loss_Area_Addresses.xlsx")


def create_parcel_field_drop_list():
    # Create  a list of field names to drop from Parcel output Excel files
    field_names = [
        field.name for field in arcpy.ListFields(TAX_PARCELS_GPIN) if field.name != "Shape"
    ]
    names_to_keep = [
        "GPIN",
        "ADDRESS_KE",
        "FULL_ADDRE",
        "CITY",
        "ZIP_CODE",
        "OWNER_CURR",
        "MAILING_AD",
        "MAILING__1",
        "MAILING__2",
        "MAILING__3",
        "MAGISTERIA",
    ]
    remove_set = set(names_to_keep)

    return [item for item in field_names if item not in remove_set]

def create_condo_field_drop_list():
    # Create  a list of field names to drop from the Condo Excel files
    field_names = [
        field.name
        for field in arcpy.ListFields(MASTER_ADDRESS_POINTS)
        if field.name != "Shape"
    ]
    names_to_keep = [
        "GPIN",
        "CAMA_GPIN",
        "ADDRESS_KE",
        "ADDR_TYPE",
        "ADDR_STATU",
        "HOUSE_NUMB",
        "ST_NAME_KE",
        "BLDG",
        "UNIT",
        "CITY",
        "STATE",
        "ZIPCODE",
        "FIPS",
        "FULL_ADDRE",
        "PRE_DIR",
        "ST_NAME",
        "ST_TYPE",
        "SUF_DIR",
        "MAGISTERIA",
    ]
    remove_set = set(names_to_keep)
    return [item for item in field_names if item not in remove_set]

def parcel_fema_sfha_addresses():
    # Select all the parcels that contain FEMA flooding that is Zone A or Zone AE
    fema_sfha_selected_parcels = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=TAX_PARCELS_GPIN,
        selection_type="NEW_SELECTION",
        where_clause="fema_sfha = 'T'",
    )

    # Export the selected parcels to an Excel file
    arcpy.conversion.TableToExcel(
        Input_Table=fema_sfha_selected_parcels,
        Output_Excel_File=FEMA_SFHA_PARCELS,
        Use_field_alias_as_column_header="ALIAS",
    )

    fields_to_drop = create_parcel_field_drop_list()

    # Delete unneeded fields
    df = pd.read_excel(FEMA_SFHA_PARCELS, sheet_name="Tax_Parcels_No_Cama_Data")
    df = df.drop(columns=fields_to_drop)
    df.to_excel(FEMA_SFHA_PARCELS, index=False)

def parcel_community_floodplain_addresses():
    # Select all the parcels that contain Community flooding
    community_selected_parcels = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=TAX_PARCELS_GPIN,
        selection_type="NEW_SELECTION",
        where_clause="community_flooding = 'T'",
    )

    # Export the selected parcels to an Excel file
    arcpy.conversion.TableToExcel(
        Input_Table=community_selected_parcels,
        Output_Excel_File=COMMUNITY_PARCELS,
        Use_field_alias_as_column_header="ALIAS",
    )

    fields_to_drop = create_parcel_field_drop_list()

    # Delete unneeded fields
    df = pd.read_excel(COMMUNITY_PARCELS, sheet_name="Tax_Parcels_No_Cama_Data")
    df = df.drop(columns=fields_to_drop)
    df.to_excel(COMMUNITY_PARCELS, index=False)

def condo_fema_sfha_addresses():
    # Select all parcels with a use description of 'Condominium'
    if arcpy.Exists("condos"):
        arcpy.management.Delete("condos")
    condominium_parcels = arcpy.management.MakeFeatureLayer(
        in_features=TAX_PARCELS,
        out_layer="condos",
        where_clause="USE_DESCRI = 'Condominium'",
    )

    # Select all of those buildings that are in the FEMA SFHA
    buildings_fema_sfha = arcpy.management.MakeFeatureLayer(
        in_features=BUILDINGS,
        out_layer="buildings_fema_sfha",
        where_clause="fema_sfha = 'T'",
    )

    # Select all the buildings in the parcels
    condo_buildings_in_FEMA_SFHA = arcpy.management.SelectLayerByLocation(
        in_layer=buildings_fema_sfha,
        overlap_type="INTERSECT",
        select_features=condominium_parcels,
        selection_type="SUBSET_SELECTION",
    )

    # Get a list of address_id values
    address_id_list = list(
        set(
            [row[0] for row in arcpy.da.SearchCursor(condo_buildings_in_FEMA_SFHA, ["address_id"])]
            )
        )

    # Select all the rows in the master address points that are in the address_id_list
    address_id_string = ", ".join(f"'{address}'" for address in address_id_list)

    master_address_points_selected = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=MASTER_ADDRESS_POINTS,
        selection_type="NEW_SELECTION",
        where_clause="address_id IN (" + address_id_string + ")",
    )

    # Export these to Excel
    arcpy.conversion.TableToExcel(
        Input_Table=master_address_points_selected, Output_Excel_File=FEMA_SFHA_CONDOS
    )

    fields_to_drop = create_condo_field_drop_list()

    # Delete unneeded fields
    df = pd.read_excel(FEMA_SFHA_CONDOS, sheet_name="master_address_points")
    df = df.drop(columns=fields_to_drop)
    df.to_excel(FEMA_SFHA_CONDOS, index=False)

def condo_community_floodplain_addresses():
    # Select all parcels with a use description of 'Condominium'
    if arcpy.Exists("condos"):
        arcpy.management.Delete("condos")
    condominium_parcels = arcpy.management.MakeFeatureLayer(
        in_features=TAX_PARCELS,
        out_layer="condos",
        where_clause="USE_DESCRI = 'Condominium'",
    )

    # Select all of those buildings that are in the Community Floodplain
    buildings_community_floodplain = arcpy.management.MakeFeatureLayer(
        in_features=BUILDINGS,
        out_layer="buildings_community_floodplain",
        where_clause="community_flooding = 'T'",
    )

    # Select all the buildings in the parcels
    condo_buildings_in_community_floodplain = arcpy.management.SelectLayerByLocation(
        in_layer=buildings_community_floodplain,
        overlap_type="INTERSECT",
        select_features=condominium_parcels,
        selection_type="SUBSET_SELECTION",
    )

    # Get a list of address_id values
    address_id_list = list(
        set(
            [row[0]
                for row in arcpy.da.SearchCursor(condo_buildings_in_community_floodplain, ["address_id"])])
        )

    # Select all the rows in the master address points that are in the address_id_list
    address_id_string = ", ".join(f"'{address}'" for address in address_id_list)

    master_address_points_selected = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=MASTER_ADDRESS_POINTS,
        selection_type="NEW_SELECTION",
        where_clause="address_id IN (" + address_id_string + ")",
    )

    # Export these to Excel
    arcpy.conversion.TableToExcel(
        Input_Table=master_address_points_selected, Output_Excel_File=COMMUNITY_CONDOS
    )

    fields_to_drop = create_condo_field_drop_list()

    # Delete unneeded fields
    df = pd.read_excel(COMMUNITY_CONDOS, sheet_name="master_address_points")
    df = df.drop(columns=fields_to_drop)
    df.to_excel(COMMUNITY_CONDOS, index=False)

def repetitive_loss_area_addresses():
    # Select all the parcels that have their center inside of a Repetitive Loss Area
    parcels_in_rla = arcpy.management.SelectLayerByLocation(
        in_layer=TAX_PARCELS_GPIN, 
        overlap_type="HAVE_THEIR_CENTER_IN", 
        select_features=REPETITIVE_LOSS_AREAS,
        selection_type="NEW_SELECTION")

    fields_to_drop = create_parcel_field_drop_list()

    # Export the selected parcels to an Excel file
    arcpy.conversion.TableToExcel(
        Input_Table=parcels_in_rla,
        Output_Excel_File=RLA_PARCELS,
        Use_field_alias_as_column_header="ALIAS",
    )    

    # Delete unneeded fields
    df = pd.read_excel(RLA_PARCELS, sheet_name="Tax_Parcels_No_Cama_Data")
    df = df.drop(columns=fields_to_drop)
    df.to_excel(RLA_PARCELS, index=False)

def main():

    # Check for the output folder
    if not arcpy.Exists(OUTPUT_FOLDER):
        arcpy.management.CreateFolder(
            out_folder_path="C:\\GIS\\Henrico\\Henrico_Data_2026\\outputs",
            out_name="Floodplain_Address_Lists",
        )

    # Delete any current Excel files
    for file in Path(OUTPUT_FOLDER).glob("*.xlsx"):
        if file.is_file():
            file.unlink()

    print("Extracting Parcel FEMA SFHA addresses...")
    parcel_fema_sfha_addresses()

    print("Extracting Parcel Community Floodplain addresses...")
    parcel_community_floodplain_addresses()

    print("Extracting Condo FEMA SFHA addresses...")
    condo_fema_sfha_addresses()

    print("Extracting Condo Community Floodplain addresses...")
    condo_community_floodplain_addresses()

    print("Extracting Repetitive Loss Area addresses...")
    repetitive_loss_area_addresses()

    print("Done.")


if __name__ == '__main__':
    main()