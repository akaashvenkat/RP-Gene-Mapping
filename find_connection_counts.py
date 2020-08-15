# File:             find_connection_counts.py
# Author:           Akaash Venkat, Audi Liu

from selenium import webdriver
from os.path import expanduser
import glob
import math
import os
import random
import subprocess
import sys
import time



GROUP_1_MAP = "svg_files/group1_colored_map.svg"
GROUP_2_MAP = "svg_files/group2_colored_map.svg"
GROUP_3_MAP = "svg_files/group3_colored_map.svg"
GROUP_4_MAP = "svg_files/group4_colored_map.svg"
COLOR_DETAILS_FILE = "input_files/color_details.txt"
CONNECTION_COUNTS_FILE = "info_files/connection_counts.txt"

CONNECTION_COUNTS = {}
COLOR_DETAILS = {}



def readColorDetails():
    with open(COLOR_DETAILS_FILE) as color_details_file:
        for line_content in color_details_file:
            if line_content != "\n":
                line_content = line_content.replace("\n", "")
                category = line_content.split(": ")[0]
                if category == "Specific Edges":
                    details = line_content.split(": ")[1].replace(" ", "").split(",")
                    COLOR_DETAILS[category] = (details)
                else:
                    detail = line_content.split(": ")[1]
                    COLOR_DETAILS[category] = detail
    color_details_file.close()



def getConnectionCounts(file, group_name, final_counts):
    counts = {}

    content = ""
    with open(file) as map:
        content = map.readlines()

    keys = ["Group 1 Connections", "Group 2 Connections", "Group 3 Connections", "Group 4 Connections", "Intermediate Connections"]
    for key in keys:
        counts[key] = 0

    for i in range(len(content)):
        if "<line class=\"nw_edge\"" in content[i]:
            stroke = content[i].split("stroke=\"")[1].split("\"")[0]
            if stroke == COLOR_DETAILS["Group 1 Connections"]:
                counts["Group 1 Connections"] += 1
            elif stroke == COLOR_DETAILS["Group 2 Connections"]:
                counts["Group 2 Connections"] += 1
            elif stroke == COLOR_DETAILS["Group 3 Connections"]:
                counts["Group 3 Connections"] += 1
            elif stroke == COLOR_DETAILS["Group 4 Connections"]:
                counts["Group 4 Connections"] += 1
            elif stroke == COLOR_DETAILS["D Gene Connections"]:
                counts["Intermediate Connections"] += 1

    final_counts[group_name] = counts



def writeConnectionCounts():
    os.system('touch ' + CONNECTION_COUNTS_FILE)
    conn_counts_file = open(CONNECTION_COUNTS_FILE, "w")
    conn_counts_file.write("The following indicates the number of connections each group of genes has with another group.\n\n")
    sorted_pairs = sorted(CONNECTION_COUNTS.items())
    for group, group_data in sorted_pairs:
        conn_counts_file.write(group + "\n")
        sorted_group_data = sorted(group_data.items())
        for other_group, count in sorted_group_data:
            other_group_name = other_group.split(" Connections")[0]
            if other_group_name == group:
                other_group_name = "other " + other_group_name
            conn_counts_file.write("\tNumber of connections with " + other_group_name + " Genes: " + str(count) + "\n")
    conn_counts_file.close()



def writeToFile(content, file_name):
    os.system('touch ' + file_name)
    os.system('rm ' + file_name)
    os.system('touch ' + file_name)

    file = open(file_name, "w")
    for counter in range(0, len(content)):
        file.write(str(content[counter]))
    file.close()



def main():
    readColorDetails()

    getConnectionCounts(GROUP_1_MAP, "Group 1", CONNECTION_COUNTS)
    getConnectionCounts(GROUP_2_MAP, "Group 2", CONNECTION_COUNTS)
    getConnectionCounts(GROUP_3_MAP, "Group 3", CONNECTION_COUNTS)
    getConnectionCounts(GROUP_4_MAP, "Group 4", CONNECTION_COUNTS)

    writeConnectionCounts()



if __name__ == "__main__":
    main()
