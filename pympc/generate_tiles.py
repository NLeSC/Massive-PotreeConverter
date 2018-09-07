#!/usr/bin/env python
"""
This script is used to distribute the points of a bunch of LAS/LAZ files in
different tiles. The XY extent of the different tiles match the XY extent of the
nodes of a certain level of a octree defined by the provided bounding box (z
is not required by the XY tiling). Which level of the octree is matched
depends on specified number of tiles:
 - 4 (2X2) means matching with level 1 of octree
 - 16 (4x4) means matching with level 2 of octree
 and so on.
"""

import argparse, traceback, time, os, math, multiprocessing, json
from pympc import utils

def getTileIndex(pX, pY, minX, minY, maxX, maxY, axisTiles):
    xpos = int((pX - minX) * axisTiles / (maxX - minX))
    ypos = int((pY - minY) * axisTiles / (maxY - minY))
    if xpos == axisTiles: # If it is in the edge of the box (in the maximum side) we need to put in the last tile
        xpos -= 1
    if ypos == axisTiles:
        ypos -= 1
    return (xpos, ypos)

def getTileName(xIndex, yIndex):
    return 'tile_%d_%d' % (int(xIndex), int(yIndex))

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
            (fCount, fMinX, fMinY, _, fMaxX, fMaxY, _, _, _, _, _, _, _) = utils.getPCFileDetails(inputFile)
            print ('Processing', os.path.basename(inputFile), fCount, fMinX, fMinY, fMaxX, fMaxY)
            # For the four vertices of the BBOX we get in which tile they should go
            posMinXMinY = getTileIndex(fMinX, fMinY, minX, minY, maxX, maxY, axisTiles)
            posMinXMaxY = getTileIndex(fMinX, fMaxY, minX, minY, maxX, maxY, axisTiles)
            posMaxXMinY = getTileIndex(fMaxX, fMinY, minX, minY, maxX, maxY, axisTiles)
            posMaxXMaxY = getTileIndex(fMaxX, fMaxY, minX, minY, maxX, maxY, axisTiles)

            if (posMinXMinY == posMinXMaxY) and (posMinXMinY == posMaxXMinY) and (posMinXMinY == posMaxXMaxY):
                # If they are the same the whole file can be directly copied to the tile
                tileFolder = outputFolder + '/' + getTileName(*posMinXMinY)
                if not os.path.isdir(tileFolder):
                    utils.shellExecute('mkdir -p ' + tileFolder)
                utils.shellExecute('cp ' + inputFile + ' ' + tileFolder)
            else:
                # If not, we run PDAL gridder to split the file in pieces that can go to the tiles
                tGCount = runPDALSplitter(processIndex, inputFile, outputFolder, tempFolder, minX, minY, maxX, maxY, axisTiles)
                if tGCount != fCount:
                    print ('WARNING: split version of ', inputFile, ' does not have same number of points (', tGCount, 'expected', fCount, ')')
            resultsQueue.put((processIndex, inputFile, fCount))

def runPDALSplitter(processIndex, inputFile, outputFolder, tempFolder, minX, minY, maxX, maxY, axisTiles):
    pTempFolder = tempFolder + '/' + str(processIndex)
    if not os.path.isdir(pTempFolder):
        utils.shellExecute('mkdir -p ' + pTempFolder)

    # Get the lenght required by the PDAL split filter in order to get "squared" tiles
    lengthPDAL = (maxX - minX) /  float(axisTiles)

    utils.shellExecute('pdal split -i ' + inputFile + ' -o ' + pTempFolder + '/' + os.path.basename(inputFile) + ' --origin_x=' + str(minX) + ' --origin_y=' + str(minY) + ' --length ' + str(lengthPDAL))
    tGCount = 0
    for gFile in os.listdir(pTempFolder):
        (gCount, gFileMinX, gFileMinY, _, gFileMaxX, gFileMaxY, _, _, _, _, _, _, _) = utils.getPCFileDetails(pTempFolder + '/' + gFile)
        # This tile should match with some tile. Let's use the central point to see which one
        pX = gFileMinX + ((gFileMaxX - gFileMinX) / 2.)
        pY = gFileMinY + ((gFileMaxY - gFileMinY) / 2.)
        tileFolder = outputFolder + '/' + getTileName(*getTileIndex(pX, pY, minX, minY, maxX, maxY, axisTiles))
        if not os.path.isdir(tileFolder):
            utils.shellExecute('mkdir -p ' + tileFolder)
        utils.shellExecute('mv ' + pTempFolder + '/' + gFile + ' ' + tileFolder + '/' + gFile)
        tGCount += gCount
    return tGCount


def run(inputFolder, outputFolder, tempFolder, extent, numberTiles, numberProcs):
    # Check input parameters
    if not os.path.isdir(inputFolder) and not os.path.isfile(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    elif os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    #elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
    #    raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    # Get the number of tiles per dimension (x and y)
    axisTiles = math.sqrt(numberTiles)
    if (not axisTiles.is_integer()) or (int(axisTiles) % 2):
        raise Exception('Error: Number of tiles must be the square of number which is power of 2!')
    axisTiles = int(axisTiles)

    # Create output and temporal folder
    utils.shellExecute('mkdir -p ' + outputFolder)
    utils.shellExecute('mkdir -p ' + tempFolder)

    (minX, minY, maxX, maxY) = extent.split(' ')
    minX = float(minX)
    minY = float(minY)
    maxX = float(maxX)
    maxY = float(maxY)

    if (maxX - minX) != (maxY - minY):
        raise Exception('Error: Tiling requires that maxX-minX must be equal to maxY-minY!')

    inputFiles = utils.getFiles(inputFolder, recursive=True)
    numInputFiles = len(inputFiles)
    print ('%s contains %d files' % (inputFolder, numInputFiles))

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
    numPoints = 0
    for i in range(numInputFiles):
        (processIndex, inputFile, inputFileNumPoints) = resultsQueue.get()
        numPoints += inputFileNumPoints
        print ('Completed %d of %d (%.02f%%)' % (i+1, numInputFiles, 100. * float(i+1) / float(numInputFiles)))
    # wait for all users to finish their execution
    for i in range(numberProcs):
        processes[i].join()

    # Write the tile.js file with information about the tiles
    cFile = open(outputFolder + '/tiles.js', 'w')
    d = {}
    d["NumberPoints"] = numPoints
    d["numXTiles"] = axisTiles
    d["numYTiles"] = axisTiles
    d["boundingBox"] = {'lx':minX,'ly':minY,'ux':maxX,'uy':maxY}
    cFile.write(json.dumps(d,indent=4,sort_keys=True))
    cFile.close()


def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""This script is used to distribute the points of a bunch of LAS/LAZ files in
different tiles. The XY extent of the different tiles match the XY extent of the
nodes of a certain level of a octree defined by the provided bounding box (z
is not required by the XY tiling). Which level of the octree is matched
depends on specified number of tiles:
 - 4 (2X2) means matching with level 1 of octree
 - 16 (4x4) means matching with level 2 of octree
 and so on. """)
    parser.add_argument('-i','--input',default='',help='Input data folder (with LAS/LAZ files)',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output data folder for the different tiles',type=str, required=True)
    parser.add_argument('-t','--temp',default='',help='Temporal folder where required processing is done',type=str, required=True)
    parser.add_argument('-e','--extent',default='',help='XY extent to be used for the tiling, specify as "minX minY maxX maxY". maxX-minX must be equal to maxY-minY. This is required to have a good extent matching with the octree',type=str, required=True)
    parser.add_argument('-n','--number',default='',help='Number of tiles (must be the power of 4. Example: 4, 16, 64, 256, 1024, etc.)',type=int, required=True)
    parser.add_argument('-p','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input folder: ', args.input)
    print ('Output folder: ', args.output)
    print ('Temporal folder: ', args.temp)
    print ('Extent: ', args.extent)
    print ('Number of tiles: ', args.number)
    print ('Number of processes: ', args.proc)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.output, args.temp, args.extent, args.number, args.proc)
        print( 'Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print( traceback.format_exc())

if __name__ == "__main__":
    main()
