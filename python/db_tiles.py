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
    parser.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    parser.add_argument('-l','--level',default=-1,help='If provided all files are assigned to such level. If not provided the level is obtained from the filename (if level is provided the previous files with same level are dropped from the DB if the table was already created)',type=int)
    parser.add_argument('-d','--dbname',default='',help='Postgres DB name',type=str)
    parser.add_argument('-t','--dbtable',default='',help='Table name',type=str, required=True)
    parser.add_argument('-u','--dbuser',default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass',default='',help='DB pass',type=str)
    parser.add_argument('-b','--dbhost',default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport',default='',help='DB port',type=str)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def runProcess(processIndex, tasksQueue, resultsQueue, connectionString, dbTable, srid, level = None):
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    fixedLevel = False
    if level >= 0:
        fixedLevel = True
    
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
            for fileAbsPath in utils.getFiles(tileAbsPath):
                (_, count, minX, minY, minZ, maxX, maxY, maxZ, _, _, _, _, _, _) = lasops.getPCFileDetails(fileAbsPath)
                insertStatement = """INSERT INTO """ + dbTable + """(filepath,tile,level,numberpoints,geom) VALUES (%s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, %s))"""
                if not fixedLevel:
                    level = len(os.path.basename(fileAbsPath)) - 5
                insertArgs = [fileAbsPath, os.path.basename(tileAbsPath), level, int(count), float(minX), float(minY), float(maxX), float(maxY), int(srid)]
                cursor.execute(insertStatement, insertArgs)
            resultsQueue.put((processIndex, tileAbsPath))
    connection.close()

def run(inputFolder, srid, level, dbName, dbTable, dbPass, dbUser, dbHost, dbPort, numberProcs):
    # Make connection
    connectionString = postgresops.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)
    
    # Create table if it does not exist
    cursor.execute('CREATE TABLE ' + dbTable + ' IF NOT EXISTS (filepath text, tile text, level integer, numberpoints integer, geom public.geometry(Geometry, %s)))', [srid, ])
    connection.commit()
    
    # Delete previous entries related to this level
    if level >= 0:
        cursor.execute('DELETE FROM ' + dbTable + ' WHERE level = %s', [level, ])
    connection.commit()
    connection.close()
    
    
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
            args=(i, tasksQueue, resultsQueue, connectionString, dbTable, srid, level)))
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
    print 'SRID: ', args.srid
    print 'Level: ', args.level
    print 'DB name: ', args.dbname
    print 'DB table: ', args.dbtable
    print 'DB port: ', '*'*len(args.dbpass)
    print 'DB user: ', args.dbuser
    print 'DB host: ', args.dbhost
    print 'DB port: ', args.dbport
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.srid, args.level, args.dbname, args.dbtable, args.dbpass, args.dbuser, args.dbhost, args.dbport, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()