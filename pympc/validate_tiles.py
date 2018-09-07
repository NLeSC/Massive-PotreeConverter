#!/usr/bin/env python
"""
This script is used to verify if the distribution the points of a bunch of LAS/LAZ files into
different tiles was done correctly. It will first compare the total number of points in the input
files with the number of points in the tiles. If they differ, the script will detect then which input
file was not tilled correctly.
"""
import sqlite3
import argparse, traceback, time, os, math, multiprocessing, json
from pympc import utils
from os import listdir
from os import walk

def list_files_1(directory, extension):
  return (f for f in listdir(directory) if f.endswith('.' + extension))

def list_files_2(directory, extension):
  list_of_files = {}
  for (dirpath, dirnames, filenames) in os.walk(directory):
    for filename in filenames:
        if filename.endswith(extension): 
            list_of_files[filename] = os.sep.join([dirpath, filename])
  return list_of_files

def createDB(dbLocation, dbName):
  conn = sqlite3.connect(dbLocation + '/' + dbName)
  c = conn.cursor()
  c.execute("""
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type='table' and name = 'inputDATA'
        """)
  if c.fetchone()[0] == 0:
    c.execute('CREATE TABLE inputDATA (fileName TEXT, numPoints INTEGER)')
  else:
    c.execute("""DELETE FROM inputDATA""")
    

  c.execute("""
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type='table' and name = 'tilesDATALAZ'
        """)
  if c.fetchone()[0] == 0:
    c.execute('CREATE TABLE tilesDATALAZ (filePartName TEXT, numPoints INTEGER)')
  else:
    c.execute("""DELETE FROM tilesDATALAZ""")

  return c

def run(dbLocation, dbName, inputFilesAbsPath, tilesAbsPath):
  dbCur = createDB(dbLocation, dbName)

  #input Files
  files = list_files_1(inputFilesAbsPath, "LAZ")
  filesNumPoints = list()
  for f in files:
    #(count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ) = utils.getPCFileDetails(files[f])
    (count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ) = utils.getPCFileDetails(inputFilesAbsPath + f)
    pcFileName = os.path.splitext(f)[0]
    filesNumPoints.append((pcFileName, count))  
  dbCur.executemany('INSERT INTO inputDATA VALUES (?,?)', filesNumPoints)
  dbCur.execute("""
        SELECT * from inputDATA
        """)
  print(dbCur.fetchall())

  #tiles Files
  files = list_files_1(tilesAbsPath, "LAZ")
  filesNumPoints = list()
  for f in files:
    #(count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ) = utils.getPCFileDetails(files[f])
    (count, minX, minY, minZ, maxX, maxY, maxZ, scaleX, scaleY, scaleZ, offsetX, offsetY, offsetZ) = utils.getPCFileDetails(tilesAbsPath + f)
    pcFileName = os.path.splitext(f)[0]
    filesNumPoints.append((pcFileName, count))  
  dbCur.executemany('INSERT INTO tilesDATALAZ VALUES (?,?)', filesNumPoints)
  dbCur.execute("""
        SELECT * from tilesDATALAZ
        """)
  print(dbCur.fetchall())
      
  #Get the ones that differ
  dbCur.execute('WITH numPoints as (SELECT i.fileName as fileName, i.numPoints as iNumPoints, sum(t.numPoints) as tNumPoints FROM inputData i, tilesData t where t.filePartName LIKE "%" || i.fileName || "%" GROUP BY i.filename, i.numPoints) SELECT fileName from numPoints where iNumPoints <> tNumPoints')

  print(dbCur.fetchall())
  dbCur.close()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""This script is used to verify if the distribution the points of a bunch of LAS/LAZ files into
          different tiles was done correctly. It will first compare the total number of points in the input
          files with the number of points in the tiles. If they differ, the script will detect then which input
          file was not tilled correctly.""")
    parser.add_argument('-l','--dbLocation',default='',help='Absolute path for the SQLite3 database location',type=str, required=True)
    parser.add_argument('-n','--dbName',default='',help='SQLite3 database name',type=str, required=True)
    parser.add_argument('-i','--inputFilesPath',default='',help='Absolute path for the input files',type=str, required=True)
    parser.add_argument('-t','--tilesPath',default='',help='Absolute path for the tiles',type=str, required=True)
    return parser

def main():
    args = argument_parser().parse_args()
    print ('SQLite3 database location: ', args.dbLocation)
    print ('SQLite3 database name: ', args.dbName)
    print ('Absolute path for input files: ', args.inputFilesPath)
    print ('Absolute path for the tiles: ', args.tilesPath)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.dbLocation, args.dbName, args.inputFilesPath, args.tilesPath)
        print( 'Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print( traceback.format_exc())

if __name__ == "__main__":
    main()
