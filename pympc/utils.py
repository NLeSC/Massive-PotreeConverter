#!/usr/bin/env python
"""Various methods reused in main scripts"""
import sys, os, glob2, subprocess, struct, numpy, math, multiprocessing

PC_FILE_FORMATS = ['las','laz']
OCTTREE_NODE_NUM_CHILDREN = 8

DB_NAME = 'pc_extents'
DB_TABLE_RAW = 'extent_raw'
DB_TABLE_POTREE = 'extent_potree'
DB_TABLE_POTREE_DIST = 'potree_dist'

def shellExecute(command, showOutErr = False):
    """ Execute the command in the SHELL and shows both stdout and stderr"""
    print(command)
    (out,err) = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    r = '\n'.join((out.decode("utf-8") , err.decode("utf-8")))
    if showOutErr:
        print(r)
    return r

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
    # If input element is file, return it
    if(os.path.isfile(inputElement)):
        fname,fext = os.path.splitext(inputElement)
        return [inputElement] if fext.lower() in extensions else []
    # Else, use recursive globbing
    files = []
    globpath = os.path.join(inputElement,'**') if recursive else inputElement
    for ext in extensions:
        files.extend(glob2.glob(os.path.join(globpath,'*.' + ext)))
        files.extend(glob2.glob(os.path.join(globpath,'*.' + ext.upper())))
    return list(set(files))


def getPCFileDetails(absPath):
    """ Get the details (count numPoints and extent) of a LAS/LAZ file (using LAStools, hence it is fast)"""
    count = None
    (minX, minY, minZ, maxX, maxY, maxZ) = (None, None, None, None, None, None)
    (scaleX, scaleY, scaleZ) = (None, None, None)
    (offsetX, offsetY, offsetZ) = (None, None, None)

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
    return (count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ)

def getPCFolderDetails(absPath, numProc = 1):
    """ Get the details (count numPoints and extent) of a folder with LAS/LAZ files (using LAStools)"""
    tcount = 0
    (tminx, tminy, tminz, tmaxx, tmaxy, tmaxz) =  (None, None, None, None, None, None)
    (tscalex, tscaley, tscalez) = (None, None, None)

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
            args=(tasksQueue, detailsQueue)))
        workers[-1].start()

    for i in range(numInputFiles):
        sys.stdout.write('\r')
        (count, minx, miny, minz, maxx, maxy, maxz, scalex, scaley, scalez, _, _, _) = detailsQueue.get()
        if i == 0:
            (tscalex, tscaley, tscalez) = (scalex, scaley, scalez)

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

    print()
    return (inputFiles, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, tscalex, tscaley, tscalez)

def runProcGetPCFolderDetailsWorker(tasksQueue, detailsQueue):
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
            detailsQueue.put(getPCFileDetails(job))


def getNode(binaryFile, level, data, lastInLevel, hierarchyStepSize):
    # Read a node from the binary file
    b = struct.unpack('B', binaryFile.read(1))[0]
    n = struct.unpack('I', binaryFile.read(4))[0]

    for i in range(OCTTREE_NODE_NUM_CHILDREN):
        # We will store a positive number if the child i exists, 0 otherwise
        data[level].append((1<<i) & b)

    if lastInLevel and level < (hierarchyStepSize+1): # If we have finished with current level and not in last level we go one more level deep
        if sum(data[level]):
            lastInNextLevel = (len(data[level]) - 1) - list(numpy.array(data[level]) > 0)[::-1].index(True) # We get the index of the last node in the next level which has data
            for j in range(lastInNextLevel + 1): # For all the nodes until the one with data, we read the node in the next level
                if data[level][j]:
                    data[level][j] = getNode(binaryFile, level+1, data, j == lastInNextLevel, hierarchyStepSize)
                else:
                    data[level+1].extend([0] * OCTTREE_NODE_NUM_CHILDREN) # If there is no data we still fill 0s to have consistent trees
    return n

def initHRC(hierarchyStepSize):
    data = {}
    for i in range(hierarchyStepSize+2): #In each HRC file we have info about the current level, hierarchyStepSize more, and only existence info in hierarchyStepSize+1, so total of hierarchyStepSize+2
        data[i] = []
    return data

def readHRC(hrcFileAbsPath, hierarchyStepSize):
    data = initHRC(hierarchyStepSize)
    data[0].append(getNode(open(hrcFileAbsPath, "rb"), 1, data, True, hierarchyStepSize))
    return data

def writeHRC(hrcFileAbsPath, hierarchyStepSize, data):
    oFile = open(hrcFileAbsPath, "wb")
    for i in range(hierarchyStepSize+1):
        for j in range(len(data[i])):
            if data[i][j]:
                m = data[i+1][OCTTREE_NODE_NUM_CHILDREN*j:OCTTREE_NODE_NUM_CHILDREN*(j+1)]
                mask= 0
                for k in range(OCTTREE_NODE_NUM_CHILDREN):
                    if k < len(m) and m[k]:
                        mask += 1<<k
                oFile.write(struct.pack('B', mask) + struct.pack('I', data[i][j]))
    oFile.close()

def getNodeName(level, i, parentName, hierarchyStepSize, extension):
    name_sub = ''
    if level:
        for l in range(level-1)[::-1]:
            name_sub += str((int(i / int(math.pow(OCTTREE_NODE_NUM_CHILDREN,l+1)))) % OCTTREE_NODE_NUM_CHILDREN)
        name_sub += str(i % OCTTREE_NODE_NUM_CHILDREN)
        if level < hierarchyStepSize:
            return (parentName + name_sub + '.' + extension, True)
        else:
            return (name_sub, False)
    else:
        return (parentName + '.' + extension, True)
