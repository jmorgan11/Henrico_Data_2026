"""
Script Name: run_queries.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script runs a series of queries against a database to gather information about
             parcels and buildings in relation to FEMA SFHA and Community Floodplain areas. 
             The results are printed in a structured format for analysis.
"""
from data_outside_flooding import main as parcels_in_county_main
from config import BUILDINGS, COUNTY_BOUNDARY, TAX_PARCELS

def main():
    """
    Main function to execute the queries and print the results.
    """
    result = parcels_in_county_main(
        parcels=TAX_PARCELS,
        county=COUNTY_BOUNDARY,
        buildings=BUILDINGS)

    print("Query Results:")
    for query, count in result.items():
        print(f"{query}: {count}")

if __name__ == "__main__":
    main()
