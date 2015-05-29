#!/usr/bin/env python
"""Merge the Potree OctTrees of each tile into a single one."""

import argparse, traceback, time, os, multiprocessing, struct, filecmp, json

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Merge the Potree OctTrees of each tile into a single one. This process deletes the original tiles, only one tile in the end with all the data")
    parser.add_argument('-i','--input',default='',help='Input folder with the Potree OctTrees',type=str, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def readHRC(hrcFileAbsPath):
    with open(hrcFileAbsPath, "rb") as f:
        b = f.read(1)
        n = f.read(4)
        while b != "":
    
            struct.unpack('b',b)
            struct.unpack('i',n)
            
            # read next
            b = f.read(1)
            n = f.read(4)


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

def joinOctTrees(octTree1AbsPath, octTree2AbsPath):
    result = False # Is the data properly merged
    
    cloudJS1 = octTree1AbsPath + '/cloud.js'
    cloudJS2 = octTree2AbsPath + '/cloud.js'
    
    #Check cloud.js files
    sameCloudJS = filecmp.cmp(cloudJS1, cloudJS2)
    
    hierarchyStepSize = json.loads(open(cloudJS1, 'r').read())['hierarchyStepSize']
     
    if sameCloudJS:
        # Check the data folder
        result = joinData(octTree1AbsPath + '/data/r', octTree2AbsPath + '/data/r', hierarchyStepSize, 'r') 
    return result

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

def run(inputFolder, numberProcs):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)

    # List input octrees
    # We do iterations of joining processes
    # First iteration we merge octrees 1 and 2, 3 and 4, ...
    # Second iteration we merge octrees 12 and 34, and 56 and 78, ...
    # Until there is only 1 octree
    # In each iteration we can run the jobs in parallel
            

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
