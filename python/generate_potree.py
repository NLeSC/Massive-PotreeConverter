#!/usr/bin/env python
"""Updates a level of the DB"""

import argparse, traceback, time, os, math, multiprocessing, psycopg2
from pointcloud import lasops, utils, postgresops

USERNAME = utils.getUserName()


def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create a folder structure with the data spatially sorted in XY tiles")
    parser.add_argument('-i','--input',default='',help='Input folder with the tiles',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output folder for the Potree data',type=str, required=True)
    parser.add_argument('-f','--format',default='',help='Format (LAS or LAZ)',type=str, required=True)
    parser.add_argument('-l','--levels',default='',help='Number of levels for OctTree',type=int, required=True)
    parser.add_argument('-s','--spacing',default='',help='Spacing at root level',type=int, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def runProcess(processIndex, tasksQueue, resultsQueue, outputFolder, format, levels, spacing):
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
            tileOutputFolder = outputFolder + '/' + os.path.basename(tileAbsPath)
            os.system('mkdir -p ' + tileOutputFolder)
            c = 'PotreeConverter -o ' + tileOutputFolder +  ' -l ' + str(levels) + ' --output-format ' + str(format).upper() + ' --source ' + tilesAbsPath + ' -s ' + str(spacing) + ' &> ' + tileOutputFolder + '.log'
            print c
            os.system(c)
            resultsQueue.put((processIndex, tileAbsPath)) 

def run(inputFolder, outputFolder, format, levels, spacing, numberProcs):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)

    # Create queues for the distributed processing
    tasksQueue = multiprocessing.Queue() # The queue of tasks (inputFiles)
    resultsQueue = multiprocessing.Queue() # The queue of results
    
    tilesNames = os.listdir(inputFolder)
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
            args=(i, tasksQueue, resultsQueue, outputFolder, format, levels, spacing)))
        processes[-1].start()

    # Get all the results (actually we do not need the returned values)
    for i in range(numTiles):
        resultsQueue.get()
        print 'Completed %d of %d (%.02f%%)' % (i+1, numTiles, 100. * float(i+1) / float(numTiles))
    # wait for all users to finish their execution
    for i in range(numberProcs):
        processes[i].join()
            

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output folder: ', args.output
    print 'Format: ', args.format
    print 'Levels: ', args.levels
    print 'Spacing: ', args.spacing
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output, args.format, args.levels, args.spacing, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()