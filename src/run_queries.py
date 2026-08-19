"""
Script Name: run_queries.py
Author: Jesse Morgan
Date: 2024-06-19
Description: This script runs a series of queries against a database to gather information about
             parcels and buildings in relation to FEMA SFHA and Community Floodplain areas. 
             The results are printed in a structured format for analysis.
"""
import os
import csv
from config import BUILDINGS, COUNTY_BOUNDARY, TAX_PARCELS, OUT_PATH
import community_decrease_only
import community_decrease
import community_increase_only
import community_increase
import community_no_change_only
import community_no_change
import data_outside_flooding
import data_within_flooding
import new_community_flooding
import overlap_com_fema
import parcels_in_county

def write_rows(csv_writer, result_dict):
    """
    Write the rows to a CSV file.
    
    Parameters:
        csv_writer (obj): A CSV writer object
        result_dict (OrderedDict): OrderedDict of values to write.
    """
    counter = 0
    for query, count in result_dict.items():
        if counter == 3:
            csv_writer.writerow("\n")
            counter = 0
        csv_writer.writerow([query, count])
        counter += 1
    csv_writer.writerow("\n")

def main():
    """
    Main function to execute the queries and print the results.
    """
    # Out CSV path
    csv_file = os.path.join(OUT_PATH, "query_results.csv")
    if os.path.exists(csv_file):
        os.remove(csv_file)

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(['Query', 'Count'])

        # Parcels in County Queries
        write_rows(writer, parcels_in_county.main(parcels=TAX_PARCELS,
                                                  county=COUNTY_BOUNDARY,
                                                  buildings=BUILDINGS))

        # Data Outside Flooding Queries
        write_rows(writer, data_outside_flooding.main(parcels=TAX_PARCELS,
                                                      buildings=BUILDINGS))

        # Data with flooding Queries
        write_rows(writer, data_within_flooding.main(parcels=TAX_PARCELS,
                                                     buildings=BUILDINGS))

        # Community Increase Queries
        write_rows(writer, community_increase.main(parcels=TAX_PARCELS,
                                                   buildings=BUILDINGS))

        # New Community flooding Queries
        write_rows(writer, new_community_flooding.main(parcels=TAX_PARCELS,
                                                       buildings=BUILDINGS))

        # Community Decrease Only Queries
        write_rows(writer, community_increase_only.main(parcels=TAX_PARCELS,
                                                        buildings=BUILDINGS))

        # Community Decrease Only Queries
        write_rows(writer, community_decrease_only.main(parcels=TAX_PARCELS,
                                                        buildings=BUILDINGS))

        # Community No Changes Queries
        write_rows(writer, community_no_change_only.main(parcels=TAX_PARCELS,
                                                    buildings=BUILDINGS))

        # Parcels and buildings with overlapping community and FEMA flooding.
        write_rows(writer, overlap_com_fema.main(parcels=TAX_PARCELS,
                                                 buildings=BUILDINGS))

        # Iterate through the magistrates
        for magistrate in ['Brookland', 'Tuckahoe', 'Fairfield', 'Varina', 'Three Chopt']:
            # Community Increase Queries
            writer.writerow([magistrate, ""])
            write_rows(writer, community_increase.main(parcels=TAX_PARCELS,
                                                       buildings=BUILDINGS,
                                                       magistrate=magistrate))

            # Community Decrease Queries
            write_rows(writer, community_decrease.main(parcels=TAX_PARCELS,
                                                       buildings=BUILDINGS,
                                                       magistrate=magistrate))

            # Community No Change Queries
            write_rows(writer, community_no_change.main(parcels=TAX_PARCELS,
                                                        buildings=BUILDINGS,
                                                        magistrate=magistrate))

            # New Community flooding Queries
            write_rows(writer, new_community_flooding.main(parcels=TAX_PARCELS,
                                                           buildings=BUILDINGS,
                                                           magistrate=magistrate))

            # Parcels and buildings with overlapping community and FEMA flooding.
            write_rows(writer, overlap_com_fema.main(parcels=TAX_PARCELS,
                                                     buildings=BUILDINGS,
                                                     magistrate=magistrate))   



if __name__ == "__main__":
    main()
