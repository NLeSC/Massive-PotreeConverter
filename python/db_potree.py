#!/usr/bin/env python
"""Updates/Creates a DB with the 2D extent information of the files in an Octtree.
If level is not specified it is automatically detected from each file name"""

import argparse, traceback, time, os, math, multiprocessing, psycopg2, json
import utils

USERNAME = utils.getUserName()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""Updates/Creates a DB with the 2D extent information of the files in an Octtree.
If level is not specified it is automatically detected from each file name""")
    parser.add_argument('-i','--input',default='',help='Input folder with the tiles',type=str, required=True)
    parser.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    parser.add_argument('-l','--level',default=-1,help='If provided all files are assigned to such level. If not provided the level is obtained from the filename (if level is provided the previous files with same level are dropped from the DB if the table was already created)',type=int)
    parser.add_argument('-f','--hrc',help='Use the hrc files to get the number of points instead of using LAStools and get the bounding cube for each node from recursive division of the bounding cube specified in the cloud.js (this is much faster but does not check the actual files) [default False]',default=False,action='store_true')
    parser.add_argument('-d','--dbname',default='',help='Postgres DB name',type=str)
    parser.add_argument('-t','--dbtable',default='',help='Table name',type=str, required=True)
    parser.add_argument('-u','--dbuser',default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass',default='',help='DB pass',type=str)
    parser.add_argument('-b','--dbhost',default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport',default='',help='DB port',type=str)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]. Only used if no hrc are used',type=int)
    return parser

def getChildBC(minX,minY,minZ,maxX,maxY,maxZ,childIndex):
    rX = (maxX - minX) / 2.
    rY = (maxY - minY) / 2.
    rZ = (maxZ - minZ) / 2.
    if childIndex == 0:
        return (minX,      minY,      minZ,      minX + rX, minY + rY, minZ + rZ)
    elif childIndex == 1:
        return (minX,      minY,      minZ + rZ, minX + rX, minY + rY, maxZ)
    elif childIndex == 2:
        return (minX,      minY + rY, minZ,      minX + rX, maxY,      minZ + rZ)
    elif childIndex == 3:
        return (minX,      minY + rY, minZ + rZ, minX + rX, maxY,      maxZ)
    elif childIndex == 4:
        return (minX + rX, minY,      minZ,      maxX,      minY + rY, minZ + rZ)
    elif childIndex == 5:
        return (minX + rX, minY,      minZ + rZ, maxX,      minY + rY, maxZ)
    elif childIndex == 6:
        return (minX + rX, minY + rY, minZ,      maxX,      maxY,      minZ + rZ)
    elif childIndex == 7:
        return (minX + rX, minY + rY, minZ + rZ, maxX,      maxY,      maxZ)
    else:
        raise Exception('Child index must be [0,7]!')
    
def addNode(cursor, dbTable, node, nodeAbsPath, hierarchyStepSize, extension, minX, minY, minZ, maxX, maxY, maxZ, fixedLevel, srid):
    hrcFile = node + '.hrc'
    hrc = None
    if os.path.isfile(nodeAbsPath + '/' + hrcFile):
        # Check if there is data in this node in Octtree A (we check if the HRC file for this node exist)
        hrc = utils.readHRC(nodeAbsPath + '/' + hrcFile, hierarchyStepSize)
        for level in range(hierarchyStepSize+1):
            for i in range(len(hrc[level])):
                if hrc[level][i]:
                    (childNode, isFile) = utils.getNodeName(level, i, node, hierarchyStepSize, extension)
                    relativeNode = childNode.replace(node,'').replace('.' + extension, '')
                    (lminX, lminY, lminZ, lmaxX, lmaxY, lmaxZ) = (minX, minY, minZ, maxX, maxY, maxZ)
                    for pNode in relativeNode:
                        (lminX, lminY, lminZ, lmaxX, lmaxY, lmaxZ) = getChildBC(lminX, lminY, lminZ, lmaxX, lmaxY, lmaxZ, int(pNode))
                    if isFile: 
                        insertStatement = """INSERT INTO """ + dbTable + """(filepath,level,numberpoints,minz,maxz,geom) VALUES (%s, %s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, %s))"""
                        if fixedLevel >= 0:
                            globalLevel = fixedLevel
                        else:
                            globalLevel = len(childNode) - 5
                        insertArgs = [nodeAbsPath + '/' + childNode, globalLevel, int(hrc[level][i]), lminZ, lmaxZ, lminX, lminY, lmaxX, lmaxY, int(srid)]
                        cursor.execute(insertStatement, insertArgs)
                        cursor.connection.commit()
                    else:
                        addNode(cursor, dbTable, node + childNode, nodeAbsPath + '/' + childNode, hierarchyStepSize, extension, lminX, lminY, lminZ, lmaxX, lmaxY, lmaxZ, fixedLevel, srid)       


def runProcess(processIndex, tasksQueue, resultsQueue, connectionString, dbTable, srid, level = None):
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    fixedLevel = False
    if level >= 0:
        fixedLevel = True
    
    kill_received = False
    while not kill_received:
        fileAbsPath = None
        try:
            # This call will patiently wait until new job is available
            fileAbsPath = tasksQueue.get()
        except:
            # if there is an error we will quit
            kill_received = True
        if tileAbsPath == None:
            # If we receive a None job, it means we can stop
            kill_received = True
        else:            
            (_, count, minX, minY, minZ, maxX, maxY, maxZ, _, _, _, _, _, _) = utils.getPCFileDetails(fileAbsPath)
            insertStatement = """INSERT INTO """ + dbTable + """(filepath,level,numberpoints,minz,maxz,geom) VALUES (%s, %s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, %s))"""
            if not fixedLevel:
                level = len(os.path.basename(fileAbsPath)) - 5
            insertArgs = [fileAbsPath, level, int(count), float(minZ), float(maxZ), float(minX), float(minY), float(maxX), float(maxY), int(srid)]
            cursor.execute(insertStatement, insertArgs)
            cursor.connection.commit()
            resultsQueue.put((processIndex, fileAbsPath))
    connection.close()

def run(inputFolder, srid, level, useHRC, dbName, dbTable, dbPass, dbUser, dbHost, dbPort, numberProcs):
    # Make connection
    connectionString = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)
    
    # Create table if it does not exist
    cursor.execute('CREATE TABLE IF NOT EXISTS ' + dbTable + ' (filepath text, level integer, numberpoints integer, minz double precision, maxz double precision, geom public.geometry(Geometry, %s))', [srid, ])
    connection.commit()
    
    # Delete previous entries related to this level
    if level >= 0:
        cursor.execute('DELETE FROM ' + dbTable + ' WHERE level = %s', [level, ])
    connection.commit()
    connection.close()
    
    if useHRC:
        cloudJSAbsPath = inputFolder + '/cloud.js'
        if not os.path.isfile(cloudJSAbsPath):
            raise Exception('Error: ' + cloudJSAbsPath + ' is not found!')        
        
        cloudJSData = json.loads(open(cloudJSAbsPath, 'r').read())
        hierarchyStepSize = cloudJSData['hierarchyStepSize']
        cloudJSBBox = cloudJSData['boundingBox']
        (minX,minY,minZ,maxX,maxY,maxZ) = (cloudJSBBox['lx'],cloudJSBBox['ly'],cloudJSBBox['lz'],cloudJSBBox['ux'],cloudJSBBox['uy'],cloudJSBBox['uz'])
        
        connection = psycopg2.connect(connectionString)
        cursor = connection.cursor()
        dataAbsPath = inputFolder + '/data'
        if len(os.listdir(dataAbsPath)):
            listFileRootA =  os.listdir(dataAbsPath + '/r')
            if 'r.las' in listFileRootA:
                extension = 'las'
            elif 'r.laz' in listFileRootA:
                extension = 'laz'
            else:
                raise Exception('Error: ' + __file__ + ' only compatible with las/laz format')
            addNode(cursor, dbTable, 'r', dataAbsPath + '/r', hierarchyStepSize, extension, minX, minY, minZ, maxX, maxY, maxZ, level, srid)
        else:
            raise Exception('Error: ' + dataAbsPath + ' is empty!')
        connection.close()
        
    else:
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
                args=(i, tasksQueue, resultsQueue, connectionString, dbTable, srid, level)))
            processes[-1].start()
    
        # Get all the results (actually we do not need the returned values)
        for i in range(numFiles):
            resultsQueue.get()
            print 'Completed %d of %d (%.02f%%)' % (i+1, numFiles, 100. * float(i+1) / float(numFiles))
        # wait for all users to finish their execution
        for i in range(numberProcs):
            processes[i].join()
               

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'SRID: ', args.srid
    print 'Level: ', args.level
    print 'Use HRC files: ', args.hrc
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
        run(args.input, args.srid, args.level, args.hrc, args.dbname, args.dbtable, args.dbpass, args.dbuser, args.dbhost, args.dbport, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
