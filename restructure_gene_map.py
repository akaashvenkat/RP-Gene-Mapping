# File:             restructure_gene_map.py
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



GENE_DATABASE_FILE = "info_files/gene_database.txt"
INTERMEDIATE_GENES_FILE = "info_files/intermediate_genes.txt"
GENE_COORDS_FILE = "info_files/gene_coords.txt"
GENE_GROUP_FILE = "info_files/gene_group.txt"
GENE_GROUPINGS_FILE = "info_files/gene_groupings.txt"
GROUPINGS_FILE = "input_files/grouping_details.txt"
BASE_SVG = "svg_files/original_gene_map.svg"
RESTRUCTURED_SVG = "svg_files/restructured_gene_map.svg"

GENE_LIST = []
GENE_GROUP = {}
GENE_GROUPINGS = {}
INTERMEDIATE_PAIRS = {}
B_D_PAIR = {}



def readDatabase():
    with open(GENE_DATABASE_FILE) as database_file:
        for line_content in database_file:
            if line_content != "\n":
                gene_info = []
                line_content = line_content.replace(" ", "")
                line_content = line_content.replace(")", "")
                line_content = line_content.replace("\n", "")
                temp_list = line_content.split("-",1)
                main_gene = temp_list[0]
                connecting_genes_list = temp_list[1].split(",")
                neighbors = {}
                for connecting_gene in connecting_genes_list:
                    name = connecting_gene.split("(")[0]
                    num = float(connecting_gene.split("(")[1])
                    neighbors[name] = num
                gene_info.append(main_gene)
                gene_info.append(neighbors)
                GENE_LIST.append(gene_info)
    database_file.close()



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
    group_file.close()



def readGeneGroupings():
    with open(GROUPINGS_FILE) as groupings_file:
        for line_content in groupings_file:
            if "Group" in line_content:
                line_content = line_content.replace("\n", "")
                grouping_id = int(line_content.split(": ")[0].split("Group ")[1])
                grouping_elements = line_content.split(": ")[1].split(", ")
                GENE_GROUPINGS[grouping_id] = grouping_elements
    groupings_file.close()



def readIntermediatePairs():
    with open(INTERMEDIATE_GENES_FILE) as intermediates_file:
        for line_content in intermediates_file:
            if line_content != "\n" and "The following" not in line_content:
                line_content = line_content.replace("\n", "")
                b_gene = line_content.split(" : ")[0]
                d_gene = line_content.split(" : ")[1]
                B_D_PAIR[b_gene] = d_gene
    intermediates_file.close()



def writeGeneCoords(new_pos_dict):
    os.system('touch ' + GENE_COORDS_FILE)
    gene_coords_file = open(GENE_COORDS_FILE, "w")
    gene_coords_file.write("The following pairings (Gene : Coords) indicate the coordinates of the gene in the restructured SVG file.\n\n")
    sorted_pairs = sorted(new_pos_dict.items())
    for gene, coords in sorted_pairs:
        gene_coords_file.write(gene + " : [" + str(coords[0]) + ", " +  str(coords[1]) + "]\n")
    gene_coords_file.close()



def writeGeneGroupings(groupings):
    os.system('touch ' + GENE_GROUPINGS_FILE)
    grouping_file = open(GENE_GROUPINGS_FILE, "w")
    groups = ["1", "2", "3", "4"]
    for counter in range(0, len(groups)):
        group_id = groups[counter]
        grouping_file.write("Group " + group_id + ": \n")
        grouping_file.write("---\n")
        cluster = groupings[counter]
        for gene in cluster:
            grouping_file.write(gene + "\n")
        grouping_file.write("\n\n\n")
    grouping_file.close()



def parseInput():
    os.system('clear')
    readDatabase()
    readGeneGroups()
    readGeneGroupings()
    readIntermediatePairs()



def getGene(str):
    lst1 = str.split('>')
    lst2 = lst1[1].split('<')
    return lst2[0]



def writeToFile(content, file_name):
    os.system('touch ' + file_name)
    os.system('rm ' + file_name)
    os.system('touch ' + file_name)
    file = open(file_name, "w")
    for counter in range(0, len(content)):
        file.write(str(content[counter]))
    file.close()



def classify(group1, group2, group3, group4):
    GROUP1 = group1[:]
    GROUP2 = group2[:]
    GROUP3 = group3[:]
    GROUP4 = group4[:]

    group_a_genes = GENE_GROUP["A"]
    a_list = group_a_genes[:]

    for groups in [group1, group2, group3, group4]:
        for gene in groups:
            if gene in a_list:
                a_list.remove(gene)

    next_input = a_list

    while next_input != []:
        next_input = classify_once(next_input, group1, group2, group3, group4, GROUP1, GROUP2, GROUP3, GROUP4)
        group1 = GROUP1[:]
        group2 = GROUP2[:]
        group3 = GROUP3[:]
        group4 = GROUP4[:]
    l = [GROUP1, GROUP2, GROUP3, GROUP4]
    return l



def classify_once(INPUT, group1_r, group2_r, group3_r ,group4_r, GROUP1, GROUP2, GROUP3, GROUP4):
    LONER = []
    for a_gene in INPUT:
        for i in range(0, len(GENE_LIST)):
            if str(a_gene) == str(GENE_LIST[i][0]):
                count = [0 for j in range(4)]
                confidence_level = [0 for k in range(4)]
                for gene, confidence in GENE_LIST[i][1].items():
                    if gene in group1_r:
                        count[0] += 1
                        confidence_level[0] += confidence
                    elif gene in group2_r:
                        count[1] += 1
                        confidence_level[1] += confidence
                    elif gene in group3_r:
                        count[2] += 1
                        confidence_level[2] += confidence
                    elif gene in group4_r:
                        count[3] += 1
                        confidence_level[3] += confidence

                max_count = max(count)
                max_index = [a for a, b in enumerate(count) if b == max_count]

                if count == [ 0 for num in range(4) ]:
                    LONER.append(a_gene)

                elif len(max_index) == 1:
                    if max_index[0] == 0:
                        GROUP1.append(a_gene)
                    elif max_index[0] == 1:
                        GROUP2.append(a_gene)
                    elif max_index[0] == 2:
                        GROUP3.append(a_gene)
                    elif max_index[0] == 3:
                        GROUP4.append(a_gene)

                else:
                    finalists = [confidence_level[n] for n in  max_index ]
                    max_conf = max(finalists)
                    index =  [a for a, b in enumerate(finalists) if b == max_conf]

                    group_num = max_index[index[0]]

                    if group_num == 0:
                        GROUP1.append(a_gene)
                    elif group_num == 1:
                        GROUP2.append(a_gene)
                    elif group_num == 2:
                        GROUP3.append(a_gene)
                    elif group_num == 3:
                        GROUP4.append(a_gene)

    return LONER



def update_dict(d_gene, dictionary, gene_info):
     dictionary[d_gene][0] += 1
     if gene_info[1][d_gene] >  dictionary[d_gene][2]:
         dictionary[d_gene][2] = gene_info[1][d_gene]
         dictionary[d_gene][1] = gene_info[0]



def store_pos(new_pos_dict, text_pos_dict, gene_list, A_D_final, D_B_PAIR, center_x, center_y, offset1, offset2, factor, radius_factor):
    radius = len(gene_list) * radius_factor
    for i in range(len(gene_list)):
        x = int(round(center_x  + radius * math.cos(6.28/len(gene_list)*i) ))
        y = int(round(center_y + radius * math.sin(6.28/len(gene_list)*i) ))
        new_pos_dict[gene_list[i]] = [ str(x), str(y) ]

        text_pos_dict[gene_list[i]] = [str(int(offset1 * x - offset2 * center_x)), str(int(offset1 * y - offset2 * center_y))]

        if gene_list[i] in A_D_final.keys():

            offset1 = factor * offset1
            offset2 = offset1 - 1

            d_gene_per_a = len(A_D_final[gene_list[i]])
            if d_gene_per_a == 1:
                d_gene = A_D_final[gene_list[i]][0]
                radius_d = radius * 1.2
                d_x = int(round(center_x  + radius_d * math.cos(6.28/len(gene_list)*i) ))
                d_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*i) ))
                new_pos_dict[d_gene] = [ str(d_x), str(d_y) ]
                text_pos_dict[d_gene] = [str(int(offset1 * d_x - offset2 * center_x)), str(int(offset1 * d_y - offset2 * center_y))]

                b_gene = D_B_PAIR[d_gene]
                radius_d = radius_d * 1.1
                b_x = int(round(center_x  + radius_d * math.cos(6.28/len(gene_list)*i) ))
                b_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*i) ))
                new_pos_dict[b_gene] = [ str(b_x), str(b_y) ]
                text_pos_dict[b_gene] = [str(int(offset1 * b_x - offset2 * center_x)), str(int(offset1 * b_y - offset2 * center_y))]

            elif d_gene_per_a > 1:
                angle_1 = i - 0.25
                for k in range(d_gene_per_a):
                    angle = angle_1 + k * 0.5/(d_gene_per_a -1)
                    d_gene = A_D_final[gene_list[i]][k]
                    radius_d = radius * 1.2

                    d_x = int(round(center_x + radius_d * math.cos(6.28/len(gene_list)*angle) ))
                    d_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*angle) ))
                    new_pos_dict[d_gene] = [ str(d_x), str(d_y) ]
                    text_pos_dict[d_gene] = [str(int(offset1 * d_x - offset2 * center_x)), str(int(offset1 * d_y - offset2 * center_y))]

                    b_gene = D_B_PAIR[d_gene]
                    radius_d = radius_d * 1.1
                    b_x = int(round(center_x + radius_d * math.cos(6.28/len(gene_list)*angle) ))
                    b_y = int(round(center_y+ radius_d * math.sin(6.28/len(gene_list)*angle) ))
                    new_pos_dict[b_gene] = [ str(b_x), str(b_y) ]
                    text_pos_dict[b_gene] = [str(int(offset1 * b_x - offset2 * center_x)), str(int(offset1 * b_y - offset2 * center_y))]

            offset1 = offset1 / factor
            offset2 = offset1 - 1



def modify_svg_content(content, old_pos_dict, new_pos_dict, text_pos_dict, GROUP1, GROUP2, GROUP3, GROUP4):
    for i in range(len(content)):
        if "font-size:" in content[i] and "px;" in content[i]:
            content[i] = ""

        if "r=\"20\"" in content[i]:
            content[i] = content[i].replace("r=\"20\"", "r=\"4\"")

        if "line class=\"nw_edge\"" in content[i] and ".0\" stroke=" in content[i]:
            content[i] = ""

        if "line class=\"nw_edge\"" in content[i] and ((".1\" stroke=" in content[i]) or (".2\" stroke=" in content[i])): #updating the edge pos
            old_width = float(content[i].split("stroke-width=\"")[1].split("\"")[0])
            old_opacity = float(content[i].split("stroke-opacity=\"")[1].split("\"")[0])
            new_width = str(0.45 * old_width)
            new_opacity = str(0.45 * old_opacity)

            old_x1 = content[i].split("x1=\"")[1].split("\"")[0]
            old_y1 = content[i].split("y1=\"")[1].split("\"")[0]
            old_x2 = content[i].split("x2=\"")[1].split("\"")[0]
            old_y2 = content[i].split("y2=\"")[1].split("\"")[0]

            mod_old_x1 = str(float(old_x1) - 0.5)
            mod_old_x2 = str(float(old_x2) - 0.5)
            mod_old_y1 = str(float(old_y1) - 0.5)
            mod_old_y2 = str(float(old_y2) - 0.5)

            if ".0" in mod_old_x1:
                mod_old_x1 = mod_old_x1[:-2]
            if ".0" in mod_old_x2:
                mod_old_x2 = mod_old_x2[:-2]
            if ".0" in mod_old_y1:
                mod_old_y1 = mod_old_y1[:-2]
            if ".0" in mod_old_y2:
                mod_old_y2 = mod_old_y2[:-2]

            gene1_name = old_pos_dict[str(mod_old_x1) + " " + str(mod_old_y1)]
            gene2_name = old_pos_dict[str(mod_old_x2) + " " + str(mod_old_y2)]

            if gene1_name in new_pos_dict and gene2_name in new_pos_dict:
                new_pos1 = new_pos_dict[gene1_name]
                new_pos2 = new_pos_dict[gene2_name]
                updated_new_pos1 = [str(float(new_pos1[0]) + 0.5), str(float(new_pos1[1]) + 0.5)]
                updated_new_pos2 = [str(float(new_pos2[0]) + 0.5), str(float(new_pos2[1]) + 0.5)]
                first_half = content[i].split("stroke-opacity=\"")[0]
                content[i] = first_half + "stroke-opacity=\"" + new_opacity + "\" stroke-width=\"" + new_width + "\" style=\"\""  +" x1=\"" + updated_new_pos1[0] + "\" y1=\"" + updated_new_pos1[1] + "\" x2=\"" + updated_new_pos2[0] + "\" y2=\"" + updated_new_pos2[1] + "\" />" + "\n"

        if "<circle cx" in content[i]:
            old_x = content[i].split("cx=\"")[1].split("\"")[0]
            old_y = content[i].split("cy=\"")[1].split("\"")[0]
            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                first_half = content[i].split(" cx=")[0]
                second_half = content[i].split("fill=")[1]
                content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" fill=" + second_half

        if "<circle class" in content[i]:
            old_x = content[i].split("cx=\"")[1].split("\"")[0]
            old_y = content[i].split("cy=\"")[1].split("\"")[0]
            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                first_half = content[i].split(" cx=")[0]
                second_half = content[i].split("display=")[1]
                content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" display=" + second_half

        if "<text " in content[i]:
            old_text_x = content[i].split(" x=\"")[1].split("\"")[0]
            old_text_y = content[i].split(" y=\"")[1].split("\"")[0]
            old_x = str(float(old_text_x) - 18)
            old_y = str(float(old_text_y) + 18)

            if ".0" in old_x:
                old_x = old_x[:-2]
            if ".0" in old_y:
                old_y = old_y[:-2]

            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                new_text_pos = text_pos_dict[gene_name]

                font_size = 17
                if gene_name in GROUP1:
                    font_size = 20
                elif gene_name in GROUP2:
                    font_size = 15
                elif gene_name in GROUP3:
                    font_size = 20
                elif gene_name in GROUP4:
                    font_size = 18

                first_half = content[i].split("x=")[0]
                first_half = first_half.replace("start", "middle") + "font-size=\"" + str(font_size) + "px\" "
                second_half = "x=\"" + new_text_pos[0] + "\" y=\"" + new_text_pos[1] + "\" alignment-baseline=\"central\">" + gene_name + "</text>\n"

                content[i] = first_half + second_half
    return content



def modify_base_svg(groups_expanded):

    with open(BASE_SVG) as base:
        content = base.readlines()

    content[0] = "<svg class=\"notselectable\" height=\"5000\" id=\"svg_network_image\" width=\"3500\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">"

    height = 5000
    width = 3500

    old_pos_dict = {}
    new_pos_dict = {}
    text_pos_dict = {}

    GROUP1 = groups_expanded[0]
    GROUP2 = groups_expanded[1]
    GROUP3 = groups_expanded[2]
    GROUP4 = groups_expanded[3]

    d_list = GENE_GROUP["D"]
    a_list = GENE_GROUP["A"]

    D_A_1 = {}
    D_A_2 = {}
    D_A_3 = {}
    D_A_4 = {}
    for d_gene in d_list:
         D_A_1[d_gene] = [0, "", 0.0]
         D_A_2[d_gene] = [0, "", 0.0]
         D_A_3[d_gene] = [0, "", 0.0]
         D_A_4[d_gene] = [0, "", 0.0]

    for i in range(len(GENE_LIST)):
        gene_info = GENE_LIST[i]
        a_gene = gene_info[0]
        genes = gene_info[1].keys()
        for d_gene in d_list:
            if d_gene in genes:
                if a_gene in GROUP1:
                    update_dict(d_gene, D_A_1, gene_info)
                elif a_gene in GROUP2:
                    update_dict(d_gene, D_A_2, gene_info)
                elif a_gene in GROUP3:
                    update_dict(d_gene, D_A_3, gene_info)
                elif a_gene in GROUP4:
                    update_dict(d_gene, D_A_4, gene_info)

    A_D_final = {}
    for a_gene in a_list:
        A_D_final[a_gene] = []

    dict_list = []
    dict_list.append(D_A_1)
    dict_list.append(D_A_2)
    dict_list.append(D_A_3)
    dict_list.append(D_A_4)
    for d_gene in d_list:
        counts = [dic[d_gene][0] for dic in dict_list]
        max_count = max(counts)
        max_index = [a for a, b in enumerate(counts) if b == max_count]

        if len(max_index) == 1:
            a_gene = dict_list[max_index[0]][d_gene][1]
            A_D_final[a_gene].append(d_gene)

        else:
            dict_list_final = [dict_list[k] for k in max_index]
            confidence_levels = [dic[d_gene][2] for dic in dict_list_final ]
            max_conf = max(confidence_levels)
            index =  [a for a, b in enumerate(confidence_levels) if b == max_conf]
            group_num = max_index[index[0]]

            a_gene = dict_list[group_num][d_gene][1]
            A_D_final[a_gene].append(d_gene)

    D_B_PAIR = {v: k for k, v in B_D_PAIR.items()}

    GROUP1.remove("RBP3")
    GROUP1.remove("FDFT1")
    GROUP1.insert(2,"RBP3")
    GROUP1.insert(4,"FDFT1")

    GROUP2.remove("EMC1")
    GROUP2.remove("ALB")
    GROUP2.append("EMC1")
    GROUP2.insert(51,"ALB")

    reposition_genes = ["ALB", "ENO4", "NEK2", "AKT1", "RHO", "PDE6A", "GAPDH", "STAT3"]
    for gene in reposition_genes:
        GROUP2.remove(gene)
    for gene in reposition_genes:
        GROUP2.insert(len(GROUP2)-1, gene)

    reposition_genes = ["SC5D", "MSMO1", "HSD17B7", "CYP51A1", "RCVRN"]
    for gene in reposition_genes:
        GROUP2.remove(gene)
    for gene in reposition_genes:
        GROUP2.insert(len(GROUP2)-16, gene)

    store_pos(new_pos_dict, text_pos_dict, GROUP1, A_D_final, D_B_PAIR, 1750, 400, 1.45, 0.45, 1.34, 12)
    store_pos(new_pos_dict, text_pos_dict, GROUP2, A_D_final, D_B_PAIR, 1750, 1600, 1.05, 0.05, 0.99, 11)
    store_pos(new_pos_dict, text_pos_dict, GROUP3, A_D_final, D_B_PAIR, 1750, 2900, 1.25, 0.25, 1.11, 12)
    store_pos(new_pos_dict, text_pos_dict, GROUP4, A_D_final, D_B_PAIR, 1750, 3950, 1.09, 0.09, 0.95, 12)

    for i in range(len(content)):
        gene_name = ""

        if "ellipse cx=" in content[i]:
            content[i] = ""

        if "g class=\"nwnodecontainer\"" in content[i] and "data-safe_div_label" in content[i]:
            gene_name = content[i].split("data-safe_div_label=\"")[1].split("\"")[0]
            x_pos = content[i].split("data-x_pos=\"")[1].split("\"")[0]
            y_pos = content[i].split("data-y_pos=\"")[1].split("\"")[0]
            old_pos_dict[x_pos + " " + y_pos] = gene_name

    content = modify_svg_content(content, old_pos_dict, new_pos_dict, text_pos_dict, GROUP1, GROUP2, GROUP3, GROUP4)
    writeToFile(content, RESTRUCTURED_SVG)
    writeGeneCoords(new_pos_dict)



def main():
    parseInput()
    groups = classify(GENE_GROUPINGS[1], GENE_GROUPINGS[2], GENE_GROUPINGS[3], GENE_GROUPINGS[4])
    writeGeneGroupings(groups)
    modify_base_svg(groups)



if __name__ == "__main__":
    main()
