"""
Script Name: config.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script contains configuration settings for the project, 
             including database connection parameters and 
             other constants used throughout the codebase.
"""
import os

DATABASE_PATH = r'C:\GIS\Henrico\Henrico_Data_2026\arcgis_pro\Henrico_2026.gdb'

BUILDINGS = os.path.join(DATABASE_PATH, 'buildings_2025')
COMMUNITY_FLOODING = os.path.join(DATABASE_PATH, 'community_sfha_boundaries')
PREVIOUS_COMMUNITY_FLOODING = os.path.join(DATABASE_PATH, 'previous_community_sfha_boundaries')
COUNTY_BOUNDARY = os.path.join(DATABASE_PATH, 'county_boundary')
FEMA_FLOODING = os.path.join(DATABASE_PATH, 'fema_s_fld_haz_ar')
FEMA_COMM_FLOODING = os.path.join(DATABASE_PATH, 'fema_comm_fld_haz_ar')
TAX_PARCELS = os.path.join(DATABASE_PATH, 'Tax_Parcels_and_CAMA_Data_Internal')
