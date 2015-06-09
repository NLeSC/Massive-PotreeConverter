#!/usr/bin/env python
"""Various methods reused in main scripts"""

import os, sys, subprocess, multiprocessing
import liblas
from osgeo import osr

PC_FILE_FORMATS = ['las','laz']

def shellExecute(command, showOutErr = False):
    """ Execute the command in the SHELL and shows both stdout and stderr"""
    print command
    (out,err) = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    r = '\n'.join((out,err))
    if showOutErr:
        print r
    return r

# Check the LAStools is installed and that it is in PATH before libLAS
if shellExecute('lasinfo -version').count('LAStools') == 0:
    raise Exception("LAStools is not found!. Please check that it is in PATH and that it is before libLAS")

def getUserName():
    return os.popen('whoami').read().replace('\n','')

def getConnectString(dbName = None, userName= None, password = None, dbHost = None, dbPort = None, cline = False):
    """ Gets the connection string to be used by psycopg2 (if cline is False)
    or by psql (if cline is True)"""
    connString=''
    if cline:    
        if dbName != None and dbName != '':
            connString += " " + dbName
        if userName != None and userName != '':
            connString += " -U " + userName
        if password != None and password != '':
            os.environ['PGPASSWORD'] = password
        if dbHost != None and dbHost != '':
            connString += " -h " + dbHost
        if dbPort != None and dbPort != '':
            connString += " -p " + dbPort
    else:
        if dbName != None and dbName != '':
            connString += " dbname=" + dbName
        if userName != None and userName != '':
            connString += " user=" + userName
        if password != None and password != '':
            connString += " password=" + password
        if dbHost != None and dbHost != '':
            connString += " host=" + dbHost
        if dbPort != None and dbPort != '':
            connString += " port=" + dbPort
    return connString

def getFiles(inputElement, extensions = PC_FILE_FORMATS, recursive = False):
    """ Get the list of files with certain extensions contained in the folder (and possible 
subfolders) given by inputElement. If inputElement is directly a file it 
returns a list with only one element, the given file """
    # If extensions is not a list but a string we converted to a list
    if type(extensions) == str:
        extensions = [extensions,]

    inputElementAbsPath = os.path.abspath(inputElement)
    if os.path.isdir(inputElementAbsPath):
        elements = sorted(os.listdir(inputElementAbsPath), key=str.lower)
        absPaths=[]
        for element in elements:
            elementAbsPath = os.path.join(inputElementAbsPath,element) 
            if os.path.isdir(elementAbsPath):
                if recursive:
                    absPaths.extend(getFiles(elementAbsPath, extensions))
            else: #os.path.isfile(elementAbsPath)
                isValid = False
                for extension in extensions:
                    if elementAbsPath.endswith(extension):
                        isValid = True
                if isValid:
                    absPaths.append(elementAbsPath)
        return absPaths
    elif os.path.isfile(inputElementAbsPath):
        isValid = False
        for extension in extensions:
            if inputElementAbsPath.endswith(extension):
                isValid = True
        if isValid:
            return [inputElementAbsPath,]
    else:
        raise Exception("ERROR: inputElement is neither a valid folder nor file")
    return []    


def getSRID(absPath):
    """ Gets the SRID of a LAS/LAZ file (using liblas and GDAL, hence it is not fast)"""
    lasHeader = liblas.file.File(absPath, mode='r').header
    osrs = osr.SpatialReference()
    osrs.SetFromUserInput(lasHeader.get_srs().get_wkt())
    #osrs.AutoIdentifyEPSG()
    return osrs.GetAttrValue( 'AUTHORITY', 1 )
        
def getPCFileDetails(absPath, srid = None):
    """ Get the details (count numPoints and extent) of a LAS/LAZ file (using LAStools, hence it is fast)"""
    count = None
    (minX, minY, minZ, maxX, maxY, maxZ) = (None, None, None, None, None, None)
    (scaleX, scaleY, scaleZ) = (None, None, None)
    (offsetX, offsetY, offsetZ) = (None, None, None)
    
    if srid == None:
        srid = getSRID(absPath)
    command = 'lasinfo ' + absPath + ' -nc -nv -nco'
    for line in shellExecute(command).split('\n'):
        if line.count('min x y z:'):
            [minX, minY, minZ] = line.split(':')[-1].strip().split(' ')
            minX = float(minX)
            minY = float(minY)
            minZ = float(minZ)
        elif line.count('max x y z:'):
            [maxX, maxY, maxZ] = line.split(':')[-1].strip().split(' ')
            maxX = float(maxX)
            maxY = float(maxY)
            maxZ = float(maxZ)
        elif line.count('number of point records:'):
            count = int(line.split(':')[-1].strip())
        elif line.count('scale factor x y z:'):
            [scaleX, scaleY, scaleZ] = line.split(':')[-1].strip().split(' ')
            scaleX = float(scaleX)
            scaleY = float(scaleY)
            scaleZ = float(scaleZ)
        elif line.count('offset x y z:'):
            [offsetX, offsetY, offsetZ] = line.split(':')[-1].strip().split(' ')
            offsetX = float(offsetX)
            offsetY = float(offsetY)
            offsetZ = float(offsetZ)
    return (srid, count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ)

def getPCFolderDetails(absPath, srid = None, numProc = 1):
    """ Get the details (count numPoints and extent) of a folder with LAS/LAZ files (using LAStools, hence it is fast)
    It is assumed that all file shave same SRID and scale as first one"""
    tcount = 0
    (tminx, tminy, tminz, tmaxx, tmaxy, tmaxz) =  (None, None, None, None, None, None)
    (tscalex, tscaley, tscalez) = (None, None, None)
    tsrid = None
    
    if os.path.isdir(absPath):
        inputFiles = getFiles(absPath, recursive=True)
    else:
        inputFiles = [absPath,]
    
    numInputFiles = len(inputFiles)
        
    tasksQueue = multiprocessing.Queue() # The queue of tasks
    detailsQueue = multiprocessing.Queue() # The queue of results/details
    
    for i in range(numInputFiles):
        tasksQueue.put(inputFiles[i])
    for i in range(numProc): #we add as many None jobs as numProc to tell them to terminate (queue is FIFO)
        tasksQueue.put(None)
    
    workers = []
    # We start numProc users workers
    for i in range(numProc):
        workers.append(multiprocessing.Process(target=runProcGetPCFolderDetailsWorker, 
            args=(tasksQueue, detailsQueue, srid)))
        workers[-1].start()
        
    for i in range(numInputFiles):
        sys.stdout.write('\r')
        (srid, count, minx, miny, minz, maxx, maxy, maxz, scalex, scaley, scalez, _, _, _) = detailsQueue.get()
        if i == 0:
            (tscalex, tscaley, tscalez) = (scalex, scaley, scalez)
            tsrid = srid
            
        tcount += count
        if count:
            if tminx == None or minx < tminx:
                tminx = minx 
            if tminy == None or miny < tminy:
                tminy = miny
            if tminz == None or minz < tminz:
                tminz = minz
            if tmaxx == None or maxx > tmaxx:
                tmaxx = maxx
            if tmaxy == None or maxy > tmaxy:
                tmaxy = maxy
            if tmaxz == None or maxz > tmaxz:
                tmaxz = maxz
        sys.stdout.write("\rCompleted %.02f%%" % (100. * float(i) / float(numInputFiles)))
        sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.write('\rCompleted 100.00%!')
    
    # wait for all users to finish their execution
    for i in range(numProc):
        workers[i].join()
    
    print
    return (inputFiles, tsrid, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, tscalex, tscaley, tscalez)

def runProcGetPCFolderDetailsWorker(tasksQueue, detailsQueue, srid):
    kill_received = False
    while not kill_received:
        job = None
        try:
            # This call will patiently wait until new job is available
            job = tasksQueue.get()
        except:
            # if there is an error we will quit the loop
            kill_received = True
        if job == None:
            kill_received = True
        else:            
            detailsQueue.put(getPCFileDetails(job, srid))