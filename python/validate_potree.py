#!/usr/bin/env python
"""Validates that the HRC files are correct in a Potree Octtree"""

import argparse, traceback, time, os, multiprocessing
import utils, merge_potree

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Validates that the HRC files are correct in a Potree Octtree")
    parser.add_argument('-i','--input',default='',help='Input folder with the Potree Octtree',type=str, required=True)
    return parser

def getNames(node, hierarchyStepSize, extension):
    names = []
    for level in range(hierarchyStepSize+2):
        if level < (hierarchyStepSize+1):
            for i in range(len(d[level])):
                if d[level][i]:
                    names.append(merge_potree.getName(level, i, node, hierarchyStepSize, extension)[0])
    return names


def validateNode(node, nodeAbsPath, hierarchyStepSize, extension):
    hrcFile = node + '.hrc'
    hrc = None
    if not os.path.isfile(nodeAbsPath + '/' + hrcFile):
        # Check if there is data in this node in Octtree A (we check if the HRC file for this node exist)
        raise Exception(nodeAbsPath + '/' + hrcFile + ' could not be read')
    hrc = readHRC(nodeAbsPath + '/' + hrcFile, hierarchyStepSize)
    nodes = getNames(node, hierarchyStepSize, extension)
    elements = os.listdir(nodeAbsPath)
    if nodes != elements:
        raise Exception(node + ' in ' + nodeAbsPath + ' is not correct')
    for element in elements:
        if element.count(extension) == 0:
            validateNode(node + element, nodeAbsPath + '/' + element, hierarchyStepSize, extension)


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
    
    print 'The Potree Octree is correct!'
    
if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input Potree Octtree: ', args.input
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
