#!/usr/bin/env python
"""Creates a DB table with the extent information of the files in a folder"""

import argparse, traceback, time, os, multiprocessing, psycopg2
import utils

USERNAME = utils.getUserName()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""Creates a DB table with the extent information of the files in a folder""")
    parser.add_argument('-i','--input',default='',help='Input folder with the files',type=str, required=True)
    parser.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    parser.add_argument('-d','--dbname',default=utils.DB_NAME,help='Postgres DB name [default ' + utils.DB_NAME + ']',type=str)
    parser.add_argument('-u','--dbuser',default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass',default='',help='DB pass',type=str)
    parser.add_argument('-b','--dbhost',default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport',default='',help='DB port',type=str)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1].',type=int)
    return parser


def runProcess(processIndex, tasksQueue, resultsQueue, connectionString, srid):
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    kill_received = False
    while not kill_received:
        fileAbsPath = None
        try:
            # This call will patiently wait until new job is available
            fileAbsPath = tasksQueue.get()
        except:
            # if there is an error we will quit
            kill_received = True
        if fileAbsPath == None:
            # If we receive a None job, it means we can stop
            kill_received = True
        else:            
            (count, minX, minY, minZ, maxX, maxY, maxZ, _, _, _, _, _, _) = utils.getPCFileDetails(fileAbsPath)
            insertStatement = """INSERT INTO """ + utils.DB_TABLE_RAW + """(filepath,numberpoints,minz,maxz,geom) VALUES (%s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, %s))"""
            insertArgs = [fileAbsPath, int(count), float(minZ), float(maxZ), float(minX), float(minY), float(maxX), float(maxY), int(srid)]
            cursor.execute(insertStatement, insertArgs)
            cursor.connection.commit()
            resultsQueue.put((processIndex, fileAbsPath))
    connection.close()

def run(inputFolder, srid, dbName, dbPass, dbUser, dbHost, dbPort, numberProcs):
    # Make connection
    connectionString = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)
    
    # Create table if it does not exist
    cursor.execute('CREATE TABLE ' + utils.DB_TABLE_RAW + ' (filepath text, numberpoints integer, minz double precision, maxz double precision, geom public.geometry(Geometry, %s))', [srid, ])
    connection.commit()
    connection.close()
    
    # Create queues for the distributed processing
    tasksQueue = multiprocessing.Queue() # The queue of tasks (inputFiles)
    resultsQueue = multiprocessing.Queue() # The queue of results
    
    inputFiles = utils.getFiles(inputFolder, recursive=True)
    numFiles = len(inputFiles)
    
    # Add tasks/inputFiles
    for i in range(numFiles):
        tasksQueue.put(inputFiles[i])
    for i in range(numberProcs): #we add as many None jobs as numberProcs to tell them to terminate (queue is FIFO)
        tasksQueue.put(None)

    processes = []
    # We start numberProcs users processes
    for i in range(numberProcs):
        processes.append(multiprocessing.Process(target=runProcess, 
            args=(i, tasksQueue, resultsQueue, connectionString, srid)))
        processes[-1].start()

    # Get all the results (actually we do not need the returned values)
    for i in range(numFiles):
        resultsQueue.get()
        print 'Completed %d of %d (%.02f%%)' % (i+1, numFiles, 100. * float(i+1) / float(numFiles))
    # wait for all users to finish their execution
    for i in range(numberProcs):
        processes[i].join()
        
    # Create an index for the geometries
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    cursor.execute('CREATE INDEX ' + utils.DB_TABLE_RAW + '_geom ON '  + utils.DB_TABLE_RAW + ' USING GIST ( geom )')
    connection.commit()
    connection.close()

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'SRID: ', args.srid
    print 'DB name: ', args.dbname
    print 'DB user: ', args.dbuser
    print 'DB pass: ', '*'*len(args.dbpass)
    print 'DB host: ', args.dbhost
    print 'DB port: ', args.dbport
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.srid, args.dbname, args.dbpass, args.dbuser, args.dbhost, args.dbport, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
