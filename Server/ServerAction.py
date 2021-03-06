import os
import re

import numpy as np
import pandas as pd
import pydot

# import ParentheticalToDot
# from Launcher import removeDup
import ParentheticalToDot


def isDup(pairs, a, b):
    for x in pairs:
        if a in x and b in x:
            return 0
    return 1


def removeDupTriplets():
    with open("HydeToTriplets.txt") as f:
        content = f.readlines()
    result = dict()
    file = open("HydeToTriplets.txt", "w")

    for x in content:
        val = x.split()[2]
        if val in result:
            pairs = result[val]
            if isDup(pairs, x.split()[0], x.split()[1]):
                file.write(x.split()[0] + " " + x.split()[1] + " " + val + "\n")
                pairs.append(x.split()[0] + "," + x.split()[1])
            result[val] = pairs
        else:
            file.write(x.split()[0] + " " + x.split()[1] + " " + val + "\n")
            result[val] = [x.split()[0] + "," + x.split()[1]]
    file.close()
    print(result)


def parseHydeToTriplets(fileName, threshold):
    dataset = pd.read_table(fileName, delim_whitespace=True, header=None,
                            names=['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7'])

    datasetLess = dataset.loc[dataset['a7'] < threshold]
    datasetMore = dataset.loc[dataset['a7'] > threshold]

    # make 2 types of triplets from the dataset less than the threshold
    tripletsFromLess1 = datasetLess.values[:, [1, 3, 5]]
    tripletsFromLess2 = datasetLess.values[:, [1, 5, 3]]

    print(tripletsFromLess1)
    print(tripletsFromLess2)

    # Writing Triplets from Less in 2 parts
    np.savetxt('Triplets1.txt', tripletsFromLess1, fmt='%d', delimiter=" ")
    np.savetxt('Triplets2.txt', tripletsFromLess2, fmt='%d', delimiter=" ")

    # Working with dataset more than the threshold
    tripletsFromMore1 = datasetMore.values[:, [1, 3, 5]]
    np.savetxt('Triplets3.txt', tripletsFromMore1, fmt='%d', delimiter=" ")

    print(tripletsFromMore1)

    read_files = ['Triplets1.txt', 'Triplets2.txt', 'Triplets3.txt']

    with open("HydeToTriplets.txt", "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
    removeDupTriplets()


def returnParentheticalFormat(fileName):
    parentheticalFormat = ''
    for line in reversed(list(open(fileName))):
        if line.__contains__('eNewick'):
            parentheticalFormat = line[28:]
            # print(parentheticalFormat)
            # print(line.rstrip())
    return parentheticalFormat.rstrip()


def convertDotToPNG(fileName):
    (graph,) = pydot.graph_from_dot_file(fileName)
    graph.write_png('cExample1.png')


def convertDotToPNGJulia(fileName, flag=''):
    paren = returnParentheticalFormat(fileName)
    with open("NetworkParen.net", "w") as text_file:
        text_file.write(paren)
    # write it to a file
    # then use the julia command
    cmd = 'julia plot-network.jl NetworkParen.net ' + flag
    os.system(cmd)


def removeLeavesJulia(leafNodes):
    with open("leaves.txt", "w") as text_file:
        text_file.write(leafNodes)
    # write it to a file
    # then use the julia command
    cmd = 'julia remove-leaves.jl  NetworkParen.net  leaves.txt'
    os.system(cmd)
    # convert Parenthetical format to png
    cmd = 'julia plot-network.jl reduced-net.txt'
    os.system(cmd)


def parentheticalFormatToPNG(parentheticalFormat, flag=''):
    with open("NetworkParen.net", "w") as text_file:
        text_file.write(parentheticalFormat)
    # write it to a file
    # then use the julia command
    cmd = 'julia plot-network.jl NetworkParen.net ' + flag
    os.system(cmd)

    # assumes that the triplets are in the parenthetical format in hte NetworkParen.net text file


# converts
def changeRoot(flag, newRoot):
    cmd = 'julia change-root.jl NetworkParen.net ' + flag + ' ' + newRoot + ' '
    os.system(cmd)
    # convert Parenthetical format to png
    cmd = 'julia plot-network.jl new-net.txt'
    os.system(cmd)


# julia change-root.jl test.net outgroup 3

"""There is a problem in the following method. I tried the same commmand via the terminal and that generates a different
dot file as compared the same command via Python.
"""


def tripletsToDot(tripletsFName):
    cmd = 'java -jar Lev1athan.jar ' + tripletsFName + ' > cExample1.dot --nopostprocess'
    os.system(cmd)


def symbolReplacement(inputStr):
    outputStr = ""
    for i in inputStr:
        asciiVal = ord(i)
        if (47 < asciiVal < 60) or (asciiVal == 0) or 96 < asciiVal < 123 or (57 < asciiVal < 60) or (
                64 < asciiVal < 91) or asciiVal == 40 or asciiVal == 41 or asciiVal == 44 or asciiVal == 35:
            outputStr += i
        else:
            inputStr.replace(i, str(asciiVal))

            strAsciiVal = str(asciiVal)
            if len(strAsciiVal) > 2:
                outputStr += "ASC" + strAsciiVal
            elif len(strAsciiVal) > 1:
                outputStr += "ASC0" + strAsciiVal
            else:
                outputStr += "ASC00" + strAsciiVal

    return outputStr


def removeNodes(nodes):
    output = ''
    nodes = nodes.split(',')

    with open("upload.dot", "r") as text_file:
        for line in text_file:
            try:
                for n in nodes:
                    if line.__contains__(" " + n + "\n"):
                        raise Exception()
            except Exception:
                continue
            output += line

    print(output)
    with open("upload.dot", "w+") as text_file:
        text_file.write(output)


def newickToDot(newick):
    dotFomat = ParentheticalToDot.newickToActualLabels(newick)
    with open("upload.dot", "w+") as text_file:
        text_file.write(dotFomat)


def returnReducedDotFile(fileName):
    retainActualLabels2(fileName)
    dotFormat = ''
    for line in list(open('cExample1_m.dot')):
        if line.__contains__('{') or line.__contains__('}') or line.__contains__('->'):
            dotFormat += line
    return dotFormat.rstrip()


def retainActualLabelDot(fileName):
    dotFormat = ''

    for line in list(open(fileName)):
        line = re.sub(r"(1[0-9][0-9][0-9])", r"internal\1", line)

        dotFormat += line
        # if line.__contains__('{') or line.__contains__('}') or line.__contains__('->'):
        #     dotFormat += line

    with open('cExample1_m.dot', 'w+') as f:
        f.write(dotFormat)


def retainActualLabels2(fileName):
    dotFormat = ''
    dictionary = {}

    for line in list(open(fileName)):
        temp = re.search(r'("[0-9]+)', line)
        if temp:
            actualName = temp.group(1)
            temp2 = re.search(r'(\d+[\s]\[)', line)
            fakeName = temp2.group(1)
            # print(found[1] + "  :  " + found2[:-1])

            dictionary[fakeName[:-1].strip()] = actualName[1]

    print(dictionary)
    # newLine = ''
    # for line in open(fileName):
    with open(fileName, 'r') as file:
        fileStr = file.read()

    for key, value in dictionary.items():
        # newLine = line.replace(key, value)
        fileStr = fileStr.replace("\n" + key + " ", "\n" + value + "Δ ")
        fileStr = fileStr.replace(" " + key + "\n", " " + value + "Δ\n")

    fileStr = fileStr.replace('Δ', '')
    dotFormat = fileStr

    with open('cExample1_m.dot', 'w+') as f:
        f.write(dotFormat)

    retainActualLabelDot('cExample1_m.dot')


if __name__ == '__main__':
    print("Hello")

    matrix = [[0 for x in range(3)] for y in range(3)]

    print(matrix)