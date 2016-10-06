#!/usr/bin/env python
"""Validates that the HRC files are correct in a Potree Octtree"""

import argparse, traceback, time, os, json
from pympc import utils

def getNames(node, hierarchyStepSize, data, extension):
    names = []
    for level in range(hierarchyStepSize+2):
        if level < (hierarchyStepSize+1):
            for i in range(len(data[level])):
                if data[level][i]:
                    names.append(utils.getNodeName(level, i, node, hierarchyStepSize, extension)[0])
    return names

def validateNode(node, nodeAbsPath, hierarchyStepSize, extension):
    hrcFile = node + '.hrc'
    hrc = None
    if not os.path.isfile(nodeAbsPath + '/' + hrcFile):
        # Check if there is data in this node in Octtree A (we check if the HRC file for this node exist)
        raise Exception(nodeAbsPath + '/' + hrcFile + ' could not be read')
    hrc = utils.readHRC(nodeAbsPath + '/' + hrcFile, hierarchyStepSize)
    for level in range(hierarchyStepSize+1):
        hrcLevel = hrc[level]
        for i in range(len(hrcLevel)):
            hrcNumPoints = hrcLevel[i]
            if hrcNumPoints:
                (childNode, isFile) = utils.getNodeName(level, i, node, hierarchyStepSize, extension)
                childNodeAbsPath = nodeAbsPath + '/' + childNode
                if not os.path.exists(childNodeAbsPath):
                    print ('Error: could not find ', childNodeAbsPath)
                    raise Exception(node + ' in ' + nodeAbsPath + ' is not correct')
                if isFile:
                    fNumPoints = utils.getPCFileDetails(childNodeAbsPath)[0]
                    if hrcNumPoints != fNumPoints:
                        print ('Error: number of points in HRC (' + str(hrcNumPoints) + ') != number of points in file (' + str(fNumPoints) + ') in ' + childNodeAbsPath)
                else:
                    validateNode(node + childNode, childNodeAbsPath, hierarchyStepSize, extension)

def run(inputFolder):
    inputFolderElements = os.listdir(inputFolder)
    if 'cloud.js' not in inputFolderElements:
        raise Exception('cloud.js not found in ' + inputFolder)
    if 'data' not in inputFolderElements:
        raise Exception('data not found in ' + inputFolder)
    dataElements = os.listdir(inputFolder + '/data')
    if 'r' not in dataElements:
        raise Exception('data/r not in ' + inputFolder)
    listFileRootA =  os.listdir(inputFolder + '/data/r')
    if 'r.las' in listFileRootA:
        extension = 'las'
    elif 'r.laz' in listFileRootA:
        extension = 'laz'
    else:
        raise Exception('Error: ' + __file__ + ' only compatible with las/laz format')

    validateNode('r', inputFolder + '/data/r', json.loads(open(inputFolder + '/cloud.js', 'r').read())['hierarchyStepSize'], extension)

    print ('The Potree Octree is correct!')


def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Validates that the HRC files are correct in a Potree Octtree")
    parser.add_argument('-i','--input',default='',help='Input folder with the Potree Octtree',type=str, required=True)
    return parser


def main():
    args = argument_parser().parse_args()
    print ('Input Potree Octtree: ', args.input)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
