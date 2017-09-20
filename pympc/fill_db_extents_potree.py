#!/usr/bin/env python
import argparse, traceback, time, os, psycopg2, json
from pympc import utils

USERNAME = utils.getUserName()
COMMIT_INTERVAL = 1000

counter = 0

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

def addNodeFolder(cursor, node, nodeAbsPath, hierarchyStepSize, extension, minX, minY, minZ, maxX, maxY, maxZ, srid, tableName):
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
                        addNodeFile(cursor, [nodeAbsPath + '/' + childNode, len(childNode) - 5, int(hrc[level][i]), lminZ, lmaxZ, lminX, lminY, lmaxX, lmaxY, int(srid)], tableName)
                    else:
                        addNodeFolder(cursor, node + childNode, nodeAbsPath + '/' + childNode, hierarchyStepSize, extension, lminX, lminY, lminZ, lmaxX, lmaxY, lmaxZ, srid, tableName)

def addNodeFile(cursor, insertArgs, tableName):
    global counter
    insertStatement = "INSERT INTO " + tableName + "(filepath,level,numberpoints,minz,maxz,geom) VALUES (%s, %s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, %s))"
    cursor.execute(insertStatement, insertArgs)
    counter += 1
    if counter == COMMIT_INTERVAL:
        cursor.connection.commit()
        counter = 0


def run(inputFolder, srid, dbName, dbPass, dbUser, dbHost, dbPort, tableName):
    # Make connection
    connectionString = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()

    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)
    cloudJSAbsPath = inputFolder + '/cloud.js'
    if not os.path.isfile(cloudJSAbsPath):
        raise Exception('Error: ' + cloudJSAbsPath + ' is not found!')

    cloudJSData = json.loads(open(cloudJSAbsPath, 'r').read())
    hierarchyStepSize = cloudJSData['hierarchyStepSize']
    cloudJSBBox = cloudJSData['boundingBox']
    (minX,minY,minZ,maxX,maxY,maxZ) = (cloudJSBBox['lx'],cloudJSBBox['ly'],cloudJSBBox['lz'],cloudJSBBox['ux'],cloudJSBBox['uy'],cloudJSBBox['uz'])

    cursor.execute('CREATE TABLE ' + tableName + ' (filepath text, level integer, numberpoints integer, minz double precision, maxz double precision, geom public.geometry(Geometry, %s))', [srid, ])
    connection.commit()
    dataAbsPath = inputFolder + '/data'
    if len(os.listdir(dataAbsPath)):
        listFileRootA =  os.listdir(dataAbsPath + '/r')
        if 'r.las' in listFileRootA:
            extension = 'las'
        elif 'r.laz' in listFileRootA:
            extension = 'laz'
        else:
            raise Exception('Error: ' + __file__ + ' only compatible with las/laz format')
        addNodeFolder(cursor, 'r', dataAbsPath + '/r', hierarchyStepSize, extension, minX, minY, minZ, maxX, maxY, maxZ, srid, tableName)
    else:
        raise Exception('Error: ' + dataAbsPath + ' is empty!')

    # Commit last uncommited inserts
    connection.commit()

    # Create an index for the geometries
    cursor.execute('CREATE INDEX ' + tableName + '_geom ON '  + tableName + ' USING GIST ( geom )')
    cursor.execute('CREATE INDEX ' + tableName + '_level ON ' + tableName + ' (level)')
    connection.commit()

    # cursor.execute('CREATE TABLE ' + utils.DB_TABLE_POTREE_DIST + ' as SELECT level, count(numberpoints) as numberfiles, sum(numberpoints) as numberpoints, ((sum(numberpoints) :: float) / (SELECT sum(numberpoints) FROM ' + utils.DB_TABLE_RAW + ') :: float) as ratio FROM ' + utils.DB_TABLE_POTREE + ' GROUP BY level ORDER BY level')
    # connection.commit()

    connection.close()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""Creates a DB table with the extent information of the files in a Potree OctTree.
The files are not opened, instead we get the information from the HRC files and the
known extent of the OctTree nodes""")
    parser.add_argument('-d','--dbname',default=utils.DB_NAME,help='Postgres DB name [default ' + utils.DB_NAME + ']',type=str)
    parser.add_argument('-u','--dbuser',default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass',default='',help='DB pass',type=str)
    parser.add_argument('-b','--dbhost',default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport',default='',help='DB port',type=str)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-i','--input',default='',help='Input folder with the Potree OctTree (must contain the cloud.js file and the data folder)',type=str, required=True)
    requiredArgs.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input Potree OctTree: ', args.input)
    print ('SRID: ', args.srid)
    print ('DB name: ', args.dbname)
    print ('DB user: ', args.dbuser)
    print ('DB pass: ', '*'*len(args.dbpass))
    print ('DB host: ', args.dbhost)
    print ('DB port: ', args.dbport)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.srid, args.dbname, args.dbpass, args.dbuser, args.dbhost, args.dbport, utils.DB_TABLE_POTREE)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
