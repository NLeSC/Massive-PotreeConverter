#!/usr/bin/env python
"""Merge two Potree OctTrees into a single one."""

import argparse, traceback, time, os, multiprocessing, struct, filecmp, json

OCTTREE_NODE_NUM_CHILDREN = 8

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Merge two Potree OctTrees into a single one.")
    parser.add_argument('-a','--inputa',default='',help='Input Potree OctTree A',type=str, required=True)
    parser.add_argument('-b','--inputb',default='',help='Input Potree OctTree B',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output Potree OctTree',type=str, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def getNode(binaryFile, level, data, lastInLevel):
    # Add an empty array for a new level
    if level not in data:
        data[level] = []
    
    # Read a node from the binary file 
    b = struct.unpack('b', binaryFile.read(1))[0]
    n = struct.unpack('i', binaryFile.read(4))[0]
    
    for i in range(OCTTREE_NODE_NUM_CHILDREN):
        data[level].append(((1<<i) & b) == 1)
    
    if lastInLevel:
        lastInNextLevel = (len(data[level]) - 1) - data[level][::-1].index(True) 
        for i in range(len(data[level])):
            if data[level][i]:
                data[level][i] = getNode(binaryFile, level+1, data, i == lastInNextLevel)
                
    
    
    return n
    
    


def joinHRC(iHRCFileAbsPath1, iHRCFileAbsPath2, oHRCFileAbsPath):   
    hrc1 = open(iHRCFileAbsPath1, "rb")
    hrc2 = open(iHRCFileAbsPath2, "rb")
    
    hrc1HasNextLevel = True
    hrc2HasNextLevel = True
    
    hrc1Level = 0
    hrc2Level = 0
    
    hrc1LevelData = {}
    hrc2LevelData = {}
    
    hrc1ToReadNextLevel = 1
    hrc2ToReadNextLevel = 1
    
    while hrc1HasNextLevel or hrc2HasNextLevel:
        hrc1LevelData[hrc1Level] = []
        hrc2LevelData[hrc2Level] = []
        
        for i in range(hrc1ToReadNextLevel):
            b = hrc1.read(1) # 0000 0001
            n = hrc1.read(4)

def joinData(d1, d1, hierarchyStepSize, parentNode):
    result = False
    # open hrc file
    # read level by level and join las files when required (in temporal folder and then replace the one in octree1)
    # join with info given by hrc
    # when level is higher multiple of stepsize call joinData iteratively to go deep in the tree (add check to see if it is necessay to go deep or we can copy) 
    return result

def createCloudJS(inputFolderA, inputFolderB, outputFolder):
    result = False # Is the data properly merged
    
    cloudJSA = inputFolderA + '/cloud.js'
    cloudJSB = inputFolderB + '/cloud.js'
    
    cloudJSO = outputFolder + '/cloud.js'
    
    if not (os.path.isfile(cloudJSA)) or not (os.path.isfile(cloudJSB)):
        raise Exception('Error: Some cloud.js is missing!')  
    
    cloudJSDataA = json.loads(open(cloudJSA, 'r').read())
    cloudJSDataB = json.loads(open(cloudJSB, 'r').read())
    
    cloudJSDataO = {}
    # Compare fields in the input cloud.js's that should be equal
    # We also write the fields in the output cloud.js
    for equalField in ["version", "octreeDir", "boundingBox", "pointAttributes", "spacing", "scale", "hierarchyStepSize"]:    
        if cloudJSDataA[equalField] == cloudJSDataB[equalField]:
             cloudJSDataO[equalField] = cloudJSDataA[equalField]
        else:
            raise Exception('Error: Can not join cloud.js. Distinct ' + equalField + '!')
    
    # For the field "tightBoundingBox" we need to merge them since they can be different
    tbbA = cloudJSDataA["tightBoundingBox"]
    tbbB = cloudJSDataB["tightBoundingBox"]
    
    tbbO = {}
    tbbO["lx"] = min([tbbA["lx"], tbbB["lx"]])
    tbbO["ly"] = min([tbbA["ly"], tbbB["ly"]])
    tbbO["lz"] = min([tbbA["lz"], tbbB["lz"]])
    tbbO["ux"] = max([tbbA["ux"], tbbB["ux"]])
    tbbO["uy"] = max([tbbA["uy"], tbbB["uy"]])
    tbbO["uz"] = max([tbbA["uz"], tbbB["uz"]])
    cloudJSDataO["tightBoundingBox"] = tbbO
    
    hierarchyStepSize = cloudJSDataA['hierarchyStepSize']
    
    cloudJSOFile = open(cloudJSO, 'w')
    cloudJSOFile.write(json.dumps(cloudJSDataO))
    cloudJSOFile.close()
     
    return hierarchyStepSize

def runProcess(processIndex, tasksQueue, resultsQueue):
    kill_received = False
    while not kill_received:
        octtrees = None
        try:
            # This call will patiently wait until new job is available
            octtrees = tasksQueue.get()
        except:
            # if there is an error we will quit
            kill_received = True
        if octtrees == None:
            # If we receive a None job, it means we can stop
            kill_received = True
        else:
            (octtree1, octtree2) = octtrees
            result = joinOctTrees(octtree1, octtree2)
            resultsQueue.put((processIndex, octtree1, octtree2, result)) 

def run(inputFolderA, inputFolderB, outputFolder, numberProcs):
    # Check input parameters
    if (not os.path.isdir(inputFolderA)) or (not os.path.isdir(inputFolderB)):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    
    # Make it absolute path
    inputFolderA = os.path.abspath(inputFolderA)
    inputFolderB = os.path.abspath(inputFolderB)

    os.system('mkdir -p ' + outputFolder)
    os.system('mkdir -p ' + outputFolder + '/data')

    # Let's create the output cloud.js
    hierarchyStepSize = createCloudJS(inputFolderA, inputFolderB, outputFolder)
    
    data = {}
    
    hr1 = getNode(open(hrcFileAbsPath, "rb"), 0, data, True)

    # List input octrees
    # We do iterations of joining processes
    # First iteration we merge octrees 1 and 2, 3 and 4, ...
    # Second iteration we merge octrees 12 and 34, and 56 and 78, ...
    # Until there is only 1 octree
    # In each iteration we can run the jobs in parallel
            

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input Potree Octtree A: ', args.inputa
    print 'Input Potree Octtree B: ', args.inputb
    print 'Output Potree Octtree: ', args.output
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.inputa, args.inputb, args.output, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
