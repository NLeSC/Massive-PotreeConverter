#!/usr/bin/env python
import os, argparse, traceback, time, multiprocessing, glob
from pympc import utils

def runProcess(processIndex, tasksQueue, resultsQueue, outputFolder, useApprox):
    kill_received = False
    while not kill_received:
        tileAbsPath = None
        try:
            # This call will patiently wait until new job is available
            tileAbsPath = tasksQueue.get()
        except:
            # if there is an error we will quit
            kill_received = True
        if tileAbsPath == None:
            # If we receive a None job, it means we can stop
            kill_received = True
        else:
            tFile = open(outputFolder + '/' + os.path.basename(tileAbsPath) + '.wkt', 'w')
            (tMinX,tMinY,tMaxX,tMaxY) = (None, None, None, None)

            if os.path.isfile(tileAbsPath):
                tilefiles =  [tileAbsPath,]
            else:
                tilefiles = glob.glob(tileAbsPath + '/*')

            for tilefile in tilefiles:
                (_, fMinX, fMinY, _, fMaxX, fMaxY, _, _, _, _, _, _, _) = utils.getPCFileDetails(tilefile)
                if useApprox:
                    if tMinX == None or tMinX > fMinX:
                        tMinX = fMinX
                    if tMinY == None or tMinY > fMinY:
                        tMinY = fMinY
                    if tMaxX == None or tMaxX < fMaxX:
                        tMaxX = fMaxX
                    if tMaxY == None or tMaxY < fMaxY:
                        tMaxY = fMaxY
                else:
                    tFile.write('POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))\n' % (fMinX, fMaxY, fMinX, fMinY, fMaxX, fMinY, fMaxX, fMaxY, fMinX, fMaxY))
            if useApprox and tMinX != None:
                tFile.write('POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))\n' % (tMinX, tMaxY, tMinX, tMinY, tMaxX, tMinY, tMaxX, tMaxY, tMinX, tMaxY))
            tFile.close()
            resultsQueue.put((processIndex, tileAbsPath))

def run(inputFolder, outputFolder, numberProcs, useApprox):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')

        # Create queues for the distributed processing
    tasksQueue = multiprocessing.Queue() # The queue of tasks (inputFiles)
    resultsQueue = multiprocessing.Queue() # The queue of results

    os.system('mkdir -p ' + outputFolder)

    tilesNames = os.listdir(inputFolder)
    if 'tiles.js' in tilesNames:
        tilesNames.remove('tiles.js')
    numTiles = len(tilesNames)

     # Add tasks/inputFiles
    for i in range(numTiles):
        tasksQueue.put(inputFolder + '/' + tilesNames[i])
    for i in range(numberProcs): #we add as many None jobs as numberProcs to tell them to terminate (queue is FIFO)
        tasksQueue.put(None)

    processes = []
    # We start numberProcs users processes
    for i in range(numberProcs):
        processes.append(multiprocessing.Process(target=runProcess,
            args=(i, tasksQueue, resultsQueue, outputFolder, useApprox)))
        processes[-1].start()

    # Get all the results (actually we do not need the returned values)
    for i in range(numTiles):
        resultsQueue.get()
        print ('Completed %d of %d (%.02f%%)' % (i+1, numTiles, 100. * float(i+1) / float(numTiles)))
    # wait for all users to finish their execution
    for i in range(numberProcs):
        processes[i].join()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="From a folder full of point cloud elements (LAS/LAZ files or subfolders containing LAS/LAZ files), it create a WKT file with extent/s of the elements")
    parser.add_argument('-i','--input',default='',help='Input folder with the point cloud elements (a element can be a single LAS/LAZ file or a folder with LAS/LAZ files)',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output folder for the WKT files',type=str, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    parser.add_argument('-a','--approx',help='Only outputs one a BBOX per element instead of a BBOX per file in element (only applies if an element is a folder). [default False]',default=False,action='store_true')
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input folder: ', args.input)
    print ('Output folder: ', args.output)
    print ('Number of processes: ', args.proc)
    print ('Approximation: ', args.approx)
    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.output, args.proc, args.approx)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
