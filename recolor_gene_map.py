# File:             recolor_gene_map.py
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



GENE_GROUP_FILE = "info_files/gene_group.txt"
GENE_GROUPING_FILE = "info_files/gene_groupings.txt"
INTERMEDIATE_GENES_FILE = "info_files/intermediate_genes.txt"
GENE_COORDS_FILE = "info_files/gene_coords.txt"
COLOR_DETAILS_FILE = "input_files/color_details.txt"
RESTRUCTURED_SVG = "svg_files/restructured_gene_map.svg"

GENE_GROUP = {}
GROUP_GENE = {}
GENE_GROUPING = {}
INTERMEDIATE_PAIRS = {}
GENE_COORDS = {}
COORDS_GENE = {}
COLOR_DETAILS = {}



def readGeneGroups():
    with open(GENE_GROUP_FILE) as group_file:
        group_id = "Z"
        for line_content in group_file:
            if line_content != "\n" and "---" not in line_content:
                if "Group" in line_content and ":" in line_content:
                    group_id = line_content.split(": ")[0].split("Group ")[1]
                    GENE_GROUP[group_id] = []
                else:
                    gene = line_content.replace("\n", "")
                    GENE_GROUP[group_id].append(gene)
                    GROUP_GENE[gene] = group_id
    group_file.close()



def readGeneGroupings():
    with open(GENE_GROUPING_FILE) as grouping_file:
        grouping_id = "Z"
        for line_content in grouping_file:
            if line_content != "\n" and "---" not in line_content:
                if "Group" in line_content and ":" in line_content:
                    grouping_id = int(line_content.split(": ")[0].split("Group ")[1])
                    GENE_GROUPING[grouping_id] = []
                else:
                    gene = line_content.replace("\n", "")
                    GENE_GROUPING[grouping_id].append(gene)
    grouping_file.close()



def readIntermediatePairs():
    with open(INTERMEDIATE_GENES_FILE) as intermediates_file:
        for line_content in intermediates_file:
            if line_content != "\n" and "The following" not in line_content:
                line_content = line_content.replace("\n", "")
                b_gene = line_content.split(" : ")[0]
                d_gene = line_content.split(" : ")[1]
                INTERMEDIATE_PAIRS[b_gene] = d_gene
    intermediates_file.close()



def readGeneCoords():
    with open(GENE_COORDS_FILE) as gene_coords_file:
        for line_content in gene_coords_file:
            if line_content != "\n" and "The following" not in line_content:
                line_content = line_content.replace("\n", "")
                gene = line_content.split(" : ")[0]
                coords = [-1, -1]
                coords[0] = line_content.split("[")[1].split(",")[0]
                coords[1] = line_content.split(", ")[1].split("]")[0]
                GENE_COORDS[gene] = coords
                COORDS_GENE[coords[0] + " " + coords[1]] = gene
    gene_coords_file.close()



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



def parseInput():
    os.system('clear')
    readGeneGroups()
    readGeneGroupings()
    readIntermediatePairs()
    readGeneCoords()
    readColorDetails()



def changeGeneColor(content):
    for i in range(len(content)):
        if "<g class=\"nwnodecontainer\"" in content[i]:
            gene = content[i].split("data-safe_div_label=")[1].split(" ")[0].replace("\"", "")
            group = "Group " + GROUP_GENE[gene]
            color = COLOR_DETAILS[group]

            original_color = content[i+3].split("rgb")[1].split("\"")[0]
            content[i+3] = content[i+3].replace(original_color, color)
    return content



def changeEdgeColor(content, genes, color):
    for gene in genes:
        for i in range(len(content)):
            gene_coords = GENE_COORDS[gene]
            option1 = "x1=\"" + gene_coords[0] + ".5\" y1=\"" + gene_coords[1] + ".5\""
            option2 = "x2=\"" + gene_coords[0] + ".5\" y2=\"" + gene_coords[1] + ".5\""

            if option1 in content[i] or option2 in content[i]:
                original_color = content[i].split("stroke=\"")[1].split("\"")[0]
                original_stroke_width = content[i].split("stroke-width=\"")[1].split("\"")[0]
                original_stroke_opacity = content[i].split("stroke-opacity=\"")[1].split("\"")[0]
                content[i] = content[i].replace(original_color, color)
                content[i] = content[i].replace("stroke-opacity=\"" + original_stroke_opacity, "stroke-opacity=\"" + "0.6")
                content[i] = content[i].replace("stroke-width=\"" + original_stroke_width, "stroke-width=\"" + "1.0")
    return content



def changeSpecificEdgeColor(content, gene1, gene2, color, opacity, width):
    for i in range(len(content)):
        gene1_coords = GENE_COORDS[gene1]
        gene2_coords = GENE_COORDS[gene2]
        option1 = "x1=\"" + gene1_coords[0] + ".5\" y1=\"" + gene1_coords[1] + ".5\" x2=\"" + gene2_coords[0] + ".5\" y2=\"" + gene2_coords[1] + ".5\""
        option2 = "x1=\"" + gene2_coords[0] + ".5\" y1=\"" + gene2_coords[1] + ".5\" x2=\"" + gene1_coords[0] + ".5\" y2=\"" + gene1_coords[1] + ".5\""

        if option1 in content[i] or option2 in content[i]:
            original_color = content[i].split("stroke=\"")[1].split("\"")[0]
            original_stroke_width = content[i].split("stroke-width=\"")[1].split("\"")[0]
            original_stroke_opacity = content[i].split("stroke-opacity=\"")[1].split("\"")[0]

            content[i] = content[i].replace(original_color, color)
            content[i] = content[i].replace("stroke-opacity=\"" + original_stroke_opacity, "stroke-opacity=\"" + str(opacity))
            content[i] = content[i].replace("stroke-width=\"" + original_stroke_width, "stroke-width=\"" + str(width))
    return content



def updateEdgeColor(content, genes, matching_b_genes):

    intermediates_involved = []

    for i in range(len(content)):
        if "line class" in content[i]:
            original_color = content[i].split("stroke=\"")[1].split("\"")[0]
            content[i] = content[i].replace(original_color, "#FFFFFF")

    for gene in genes:
        for i in range(len(content)):

            if "line class" not in content[i]:
                continue

            gene_coords = GENE_COORDS[gene]
            option1 = "x1=\"" + gene_coords[0] + ".5\" y1=\"" + gene_coords[1] + ".5\""
            option2 = "x2=\"" + gene_coords[0] + ".5\" y2=\"" + gene_coords[1] + ".5\""
            other_gene = ""

            if option1 in content[i]:
                other_x = content[i].split("x2=\"")[1].split(".5\"")[0]
                other_y = content[i].split("y2=\"")[1].split(".5\"")[0]
                other_coords = other_x + " " + other_y
                other_gene = COORDS_GENE[other_coords]
            elif option2 in content[i]:
                other_x = content[i].split("x1=\"")[1].split(".5\"")[0]
                other_y = content[i].split("y1=\"")[1].split(".5\"")[0]
                other_coords = other_x + " " + other_y
                other_gene = COORDS_GENE[other_coords]
            else:
                continue

            if other_gene in GENE_GROUPING[1]:
                color = COLOR_DETAILS["Group 1 Connections"]
            elif other_gene in GENE_GROUPING[2]:
                color = COLOR_DETAILS["Group 2 Connections"]
            elif other_gene in GENE_GROUPING[3]:
                color = COLOR_DETAILS["Group 3 Connections"]
            elif other_gene in GENE_GROUPING[4]:
                color = COLOR_DETAILS["Group 4 Connections"]
            else:
                color = COLOR_DETAILS["D Gene Connections"]
                intermediates_involved.append(other_gene)

            original_color = content[i].split("stroke=\"")[1].split("\"")[0]
            content[i] = content[i].replace(original_color, color)

    intermediates_involved = list(dict.fromkeys(intermediates_involved))

    for b_gene, d_gene in INTERMEDIATE_PAIRS.items():
        if d_gene in intermediates_involved:
            gene1_coords = GENE_COORDS[b_gene]
            gene2_coords = GENE_COORDS[d_gene]
            option1 = "x1=\"" + gene1_coords[0] + ".5\" y1=\"" + gene1_coords[1] + ".5\" x2=\"" + gene2_coords[0] + ".5\" y2=\"" + gene2_coords[1] + ".5\""
            option2 = "x1=\"" + gene2_coords[0] + ".5\" y1=\"" + gene2_coords[1] + ".5\" x2=\"" + gene1_coords[0] + ".5\" y2=\"" + gene1_coords[1] + ".5\""

            for i in range(len(content)):
                if option1 in content[i] or option2 in content[i]:
                    original_color = content[i].split("stroke=\"")[1].split("\"")[0]
                    content[i] = content[i].replace(original_color, "#000000")

    for i in range(len(content)):
        if "line class" in content[i]:
            original_color = content[i].split("stroke=\"")[1].split("\"")[0]
            if original_color == "#FFFFFF":
                content[i] = ""

    return content



def writeToFile(content, file_name):
    os.system('touch ' + file_name)
    os.system('rm ' + file_name)
    os.system('touch ' + file_name)

    file = open(file_name, "w")
    for counter in range(0, len(content)):
        file.write(str(content[counter]))
    file.close()



def main():
    parseInput()
    content = ""
    with open(RESTRUCTURED_SVG) as restructured:
        content = restructured.readlines()
    content = changeGeneColor(content)

    content = changeEdgeColor(content, GENE_GROUPING[4], COLOR_DETAILS["Group 4 Connections"])
    content = changeEdgeColor(content, GENE_GROUPING[3], COLOR_DETAILS["Group 3 Connections"])
    content = changeEdgeColor(content, GENE_GROUPING[2], COLOR_DETAILS["Group 2 Connections"])
    content = changeEdgeColor(content, GENE_GROUPING[1], COLOR_DETAILS["Group 1 Connections"])

    for b_gene_1 in INTERMEDIATE_PAIRS:
        d_gene_1 = INTERMEDIATE_PAIRS[b_gene_1]
        for b_gene_2 in INTERMEDIATE_PAIRS:
            d_gene_2 = INTERMEDIATE_PAIRS[b_gene_2]
            content = changeSpecificEdgeColor(content, d_gene_1, b_gene_2, COLOR_DETAILS["D Gene Connections"], 0.5, 0.8)
            content = changeSpecificEdgeColor(content, d_gene_1, d_gene_2, COLOR_DETAILS["D Gene Connections"], 0.5, 0.8)
        content = changeSpecificEdgeColor(content, b_gene_1, d_gene_1, COLOR_DETAILS["Intermediate Connections"], 1, 3.0)

    content_1 = content[:]
    content_2 = content[:]
    content_3 = content[:]
    content_4 = content[:]

    content_1 = updateEdgeColor(content_1, GENE_GROUPING[1], [])
    content_2 = updateEdgeColor(content_2, GENE_GROUPING[2], ["CDON", "AGBL5", "TRNT1", "KIZ", "ARHGAP22", "GNA13", "REEP6", "SLC7A14", "HGSNAT"])
    content_3 = updateEdgeColor(content_3, GENE_GROUPING[3], [])
    content_4 = updateEdgeColor(content_4, GENE_GROUPING[4], ["POMGNT1"])

    writeToFile(content_1, "svg_files/group1_colored_map.svg")
    writeToFile(content_2, "svg_files/group2_colored_map.svg")
    writeToFile(content_3, "svg_files/group3_colored_map.svg")
    writeToFile(content_4, "svg_files/group4_colored_map.svg")



if __name__ == "__main__":
    main()
