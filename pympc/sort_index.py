#!/usr/bin/env python
import argparse, traceback, time, os, multiprocessing
from pympc import utils

def runProcess(processIndex, tasksQueue, resultsQueue, outputFolder, runMode, useLink):
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
            tileFilesAbsPaths = utils.getFiles(tileAbsPath, recursive = True)
            for i,tileFileAbsPath in enumerate(tileFilesAbsPaths):
                if (len(tileFilesAbsPaths) == 1) and os.path.isfile(tileAbsPath):
                    outputAbsPath = tileOutputFolder
                else:
                    if i  == 0:
                        os.system('mkdir -p ' + tileOutputFolder)
                    outputAbsPath = outputFolder + '/' + os.path.basename(tileAbsPath) + '/' + os.path.basename(tileFileAbsPath)
                commands = []
                if 's' in runMode:
                    cmd = os.environ["LASSORT"]
                    commands.append(cmd + ' -i ' + tileFileAbsPath + ' -o ' + outputAbsPath)
                else:
                    if useLink:
                        commands.append('ln -s ' + tileFileAbsPath + ' ' + outputAbsPath)
                    else:
                        commands.append('cp ' + tileFileAbsPath + ' ' + outputAbsPath)
                if 'i' in runMode:
                    commands.append('lasindex -i ' + outputAbsPath)
                for command in commands:
                    utils.shellExecute(command, True)
            resultsQueue.put((processIndex, tileAbsPath))

def run(inputFolder, outputFolder, runMode, useLink, numberProcs):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    if runMode not in ('s','i','si','is'):
        raise Exception('Error: running mode must be s, i, or si')


    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)

    utils.shellExecute('mkdir -p ' + outputFolder)

    # Create queues for the distributed processing
    tasksQueue = multiprocessing.Queue() # The queue of tasks (inputFiles)
    resultsQueue = multiprocessing.Queue() # The queue of results

    tilesNames = os.listdir(inputFolder)
    if 'tiles.js' in tilesNames:
        tilesNames.remove('tiles.js')
        utils.shellExecute('cp ' + inputFolder + '/tiles.js ' + outputFolder+ '/tiles.js')

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
            args=(i, tasksQueue, resultsQueue, outputFolder, runMode, useLink)))
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
    description="Sort and index with LAStools a folder with point cloud elements (LAS/LAZ files or subfolders containing LAS/LAZ files). The sorted/index data is copied in the output folder. To enable ")
    parser.add_argument('-i','--input',default='',help='Input folder with the point cloud elements (a element can be a single LAS/LAZ file or a folder with LAS/LAZ files)',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output folder for the sorted and indexed elements',type=str, required=True)
    parser.add_argument('-m','--mode',default='si',help='Running mode. Specify s to run only the lassort, i to run only the lasindex and si to run both. [default is si, i.e. to run both lassort and lasindex].',type=str)
    parser.add_argument('-l','--link',help='Use ln -s instead of cp when filling in the output folder. This only applies if mode is i, i.e. no sorting [default False]',default=False,action='store_true')
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input folder: ', args.input)
    print ('Output folder: ', args.output)
    print ('Mode: ', args.mode)
    print ('Use Link: ', args.link)
    print ('Number of processes: ', args.proc)

    # Check the LAStools lassort.exe is installed
    if ('s' in args.mode):
        cmd = os.environ.get("LASSORT",None)
        if(not cmd or utils.shellExecute(cmd + ' -version').count('LAStools') == 0):
            raise Exception("LAStools lassort.exe is not found!. Please define LASSORT environment variable!")
    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.output, args.mode, args.link, args.proc)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
