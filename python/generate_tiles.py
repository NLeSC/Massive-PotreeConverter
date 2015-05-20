#!/usr/bin/env python
"""This script is used to distribute the points of a bunch of LAS/LAZ files in different tiles
"""

import argparse, traceback, time, os, math, multiprocessing, json
from pointcloud import lasops

ONLY_SHOW = False

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create a folder structure with the data spatially sorted in XY tiles")
    parser.add_argument('-i','--input',default='',help='Input data folder (with LAS/LAZ files)',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output data folder for the different tiles',type=str, required=True)
    parser.add_argument('-t','--temp',default='',help='Temporal folder where required processing is done',type=str, required=True)
    parser.add_argument('-n','--number',default='',help='Number of tiles (must be the square of a number which is power of 2. Example: 4, 16, 64, 256, 1024, etc.)',type=int, required=True)
    parser.add_argument('-p','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def getTileIndex(pX, pY, minX, minY, maxX, maxY, axisTilesX, axisTilesY):
    xpos = int((pX - minX) * axisTilesX / (maxX - minX))
    ypos = int((pY - minY) * axisTilesY / (maxY - minY))
    if xpos == axisTilesX: # If it is in the edge of the box (in the maximum side) we need to put in the last tile
        xpos -= 1
    if ypos == axisTilesY:
        ypos -= 1
    return (xpos, ypos)

def getTileName(xIndex, yIndex):
    return 'tile_%d_%d' % (int(xIndex), int(yIndex))

def executeCommand(command):
    print command
    if not ONLY_SHOW:
        os.system(command)

def runProcess(processIndex, tasksQueue, resultsQueue, minX, minY, maxX, maxY, outputFolder, tempFolder, axisTiles):
    kill_received = False
    while not kill_received:
        inputFile = None
        try:
            # This call will patiently wait until new job is available
            inputFile = tasksQueue.get()
        except:
            # if there is an error we will quit
            kill_received = True
        if inputFile == None:
            # If we receive a None job, it means we can stop
            kill_received = True
        else:            
            # Get number of points and BBOX of this file
            (_, fCount, fMinX, fMinY, _, fMaxX, fMaxY, _, _, _, _, _, _, _) = lasops.getPCFileDetails(inputFile)
            print 'Processing', os.path.basename(inputFile), fCount, fMinX, fMinY, fMaxX, fMaxY
            # For the four vertices of the BBOX we get in which tile they should go
            posMinXMinY = getTileIndex(fMinX, fMinY, minX, minY, maxX, maxY, axisTiles, axisTiles)
            posMinXMaxY = getTileIndex(fMinX, fMaxY, minX, minY, maxX, maxY, axisTiles, axisTiles)
            posMaxXMinY = getTileIndex(fMaxX, fMinY, minX, minY, maxX, maxY, axisTiles, axisTiles)
            posMaxXMaxY = getTileIndex(fMaxX, fMaxY, minX, minY, maxX, maxY, axisTiles, axisTiles)

            if (posMinXMinY == posMinXMaxY) and (posMinXMinY == posMaxXMinY) and (posMinXMinY == posMaxXMaxY):
                # If they are the same the whole file can be directly copied to the tile
                executeCommand('cp ' + inputFile + ' ' + outputFolder + '/' + getTileName(*posMinXMinY))
            else:
                # If not, we run PDAL gridder to split the file in pieces that can go to the tiles
                tGCount = runPDALGridder(processIndex, inputFile, outputFolder, tempFolder, minX, minY, maxX, maxY, axisTiles, axisTiles)
                if tGCount != fCount:
                    print 'WARNING: gridded version of ', inputFile, ' does not have same number of points (', tGCount, 'expected', fCount, ')'
            resultsQueue.put((processIndex, inputFile))   

def runPDALGridder(processIndex, inputFile, outputFolder, tempFolder, minX, minY, maxX, maxY, axisTilesX, axisTilesY):
    pTempFolder = tempFolder + '/' + str(processIndex)
    if not os.path.isdir(pTempFolder):
        executeCommand('mkdir -p ' + pTempFolder)
    executeCommand('pdal grid -i ' + inputFile + ' -o ' + pTempFolder + '/' + os.path.basename(inputFile) + ' --num_x=' + str(axisTilesX) + ' --num_y=' + str(axisTilesY) + ' --min_x=' + str(minX) + ' --min_y=' + str(minY) + ' --max_x=' + str(maxX) + ' --max_y=' + str(maxY))
    tGCount = 0
    for gFile in os.listdir(pTempFolder):
        (_, gCount, gFileMinX, gFileMinY, _, gFileMaxX, gFileMaxY, _, _, _, _, _, _, _) = lasops.getPCFileDetails(pTempFolder + '/' + gFile)
        # This tile should match with some tile. Let's use the central point to see which one
        pX = gFileMinX + ((gFileMaxX - gFileMinX) / 2.)
        pY = gFileMinY + ((gFileMaxY - gFileMinY) / 2.)
        executeCommand('mv ' + pTempFolder + '/' + gFile + ' ' + outputFolder + '/' + getTileName(*getTileIndex(pX, pY, minX, minY, maxX, maxY, axisTilesX, axisTilesY)) + '/' + gFile)
        tGCount += gCount
    return tGCount
    
def run(inputFolder, outputFolder, tempFolder, numberTiles, numberProcs):
    # Check input parameters
    if not os.path.isdir(inputFolder) and not os.path.isfile(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    # Get the number of tiles per dimension (x and y)
    axisTiles = math.sqrt(numberTiles) 
    if (not axisTiles.is_integer()) or (int(axisTiles) % 2):
        raise Exception('Error: Number of tiles must be the square of number which is power of 2!')
    axisTiles = int(axisTiles)
    
    # Create output and temporal folder
    executeCommand('mkdir -p ' + outputFolder)
    executeCommand('mkdir -p ' + tempFolder)
    
    # Get the global extent and the as well as number of points and input files
    print 'Collecting information about the input data...'
    (inputFiles, _, numPoints, minX, minY, _, maxX, maxY, _, scaleX, scaleY, _) = lasops.getPCFolderDetails(inputFolder, numProc = numberProcs)
    numInputFiles = len(inputFiles)
    print '%s contains %d files with %d points. The XY extent is %.2f, %.2f, %.2f, %.2f' % (inputFolder, numInputFiles, numPoints, minX, minY, maxX, maxY)
    
    # Generate the output folder for the tiles
    for xIndex in range(axisTiles):
        for yIndex in range(axisTiles):
            executeCommand('mkdir -p ' + outputFolder + '/' + getTileName(xIndex, yIndex))

    # Create queues for the distributed processing
    tasksQueue = multiprocessing.Queue() # The queue of tasks (inputFiles)
    resultsQueue = multiprocessing.Queue() # The queue of results
    
    # Add tasks/inputFiles
    for i in range(numInputFiles):
        tasksQueue.put(inputFiles[i])
    for i in range(numberProcs): #we add as many None jobs as numberProcs to tell them to terminate (queue is FIFO)
        tasksQueue.put(None)

    processes = []
    # We start numberProcs users processes
    for i in range(numberProcs):
        processes.append(multiprocessing.Process(target=runProcess, 
            args=(i, tasksQueue, resultsQueue, minX, minY, maxX, maxY, outputFolder, tempFolder, axisTiles)))
        processes[-1].start()

    # Get all the results (actually we do not need the returned values)
    for i in range(numInputFiles):
        resultsQueue.get()
        print 'Completed %d of %d (%.02f%%)' % (i+1, numInputFiles, 100. * float(i+1) / float(numInputFiles))
    # wait for all users to finish their execution
    for i in range(numberProcs):
        processes[i].join()
                
    # Check that the number of points after tiling is the same as initial
#    numPointsTiles = 0
#    numFilesTiles = 0
#    for xIndex in range(axisTiles):
#        for yIndex in range(axisTiles):
#            (tInputFiles, _, tNumPoints, _, _, _, _, _, _, _, _, _) = lasops.getPCFolderDetails(outputFolder + '/' + getTileName(xIndex, yIndex))
#            numPointsTiles += tNumPoints
#            numFilesTiles += len(tInputFiles)
        
#    if numPointsTiles != numPoints:
#        print 'WARNING: #input_points = %d   #output_points = %d' % (numPoints, numPointsTiles)
#    else:
#        print '#input_points = #output_points = %d' % numPointsTiles
#    print '#input_files = %d   #output_files = %d' % (numInputFiles, numFilesTiles)
    
    # Write the tile.js file with information about the tiles
    cFile = open(outputFolder + '/tiles.js', 'w')
    d = {}
    d["numberPoints"] = numPoints
    d["numXTiles"] = axisTiles
    d["numYTiles"] = axisTiles
    d["boundingBox"] = {'lx':minX,'ly':minY,'ux':maxX,'uy':maxY}
    cFile.write(json.dumps(d,indent=4,sort_keys=True))
    cFile.close()

    
if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output folder: ', args.output
    print 'Temporal folder: ', args.temp
    print 'Number of tiles: ', args.number
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output, args.temp, args.number, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
