#!/usr/bin/env python
"""This script is used to distribute the points of a bunch of LAS/LAZ files in different tiles.
The tiles are generated in a way that it is possible to match them to the deepest level 
of a QuadTree structure"""

import argparse, traceback, time, os, math
import shapely
from shapely.geometry import box
from de9im.patterns import intersects, contains

ONLY_SHOW = False

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create a folder structure with the data spatially sorted in XY tiles")
    parser.add_argument('-i','--input',default='',help='Input data folder (with LAS/LAZ files)',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output data folder for the different QuadTree cells',type=str, required=True)
    parser.add_argument('-n','--number',default='',help='Number of tiles (must be the square of a number which is power of 2. Example: 4, 16, 64, 256, 1024, etc.)',type=int, required=True)
    return parser

def _relation(geom1, geom2):
    """ Returns the relationship between two geometries. 
          0 if they are disjoint, 
          1 if geom2 is completely in geom1,
          2 if geom2 is partly in geom1"""
    relation = geom1.relate(geom2)
    if not intersects.matches(relation):
        return 0 # they are disjoint
    elif contains.matches(relation):
        return 1 
    else: # there is some overlaps
        return 2

def executeCommand(command):
    print command
    if not ONLY_SHOW:
        os.system(command)

def run(inputFolder, outputFolder, numberTiles):
    
    # Check input parameters
    if not os.path.isdir(inputFolder) and not os.path.isfile(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    # Get the number of tiles per dimension (x and y)
    axisTiles = math.sqrt(numberTiles) 
    if (not axisTiles.is_integer()) or (int(axisTiles) % 2):
        raise Exception('Error: Number of tiles must be the square of number which is power of 2!')
    axisTiles = int(axisTiles)
    
    # Create output folder
    executeCommand('mkdir -p ' + outputFolder)
    
    # Get the global extent and the as well as number of points and input files
    (inputFiles, _, numPoints, minX, minY, _, maxX, maxY, _, scaleX, scaleY, _) = lasops.getPCFolderDetails(inputFolder)
    numInputFiles = len(inputFiles)

    print '%s contains %d files with %d points. The XY extent is %.2f, %.2f, %.2f, %.2f' % (inputFolder, numInputFiles, numPoints, minX, minY, maxX, maxY)
    
    # Compute the size of a tile in X and in Y
    tSizeX = (maxX - minX) / float(axisTiles)
    tSizeY = (maxY - minY) / float(axisTiles)
    
    # Generate the tiles
    # For each tile we generate:
    #   - A Shapely BBox with the extent of the tile
    #   - The empty output folder for the files that will go in that tile
    tiles = []
    for xIndex in range(axisTiles):
        for yIndex in range(axisTiles):
            tMinX = minX + (xIndex * tSizeX)
            tMaxX = minX + ((xIndex+1) * tSizeX)
            tMinY = minY + (yIndex * tSizeY)
            tMaxY = minY + ((yIndex+1) * tSizeY)
            
            tMinXGeos = tMinX
            tMaxXGeos = tMaxX
            tMinYGeos = tMinY
            tMaxYGeos = tMaxY
            # To avoid overlapping tiles
#            if xIndex < axisTiles-1:
#                tMaxXGeos -= scaleX
#            if yIndex < axisTiles-1:
#                tMaxYGeos -= scaleY

            tMinXLT = tMinX
            tMaxXLT = tMaxX
            tMinYLT = tMinY
            tMaxYLT = tMaxY

#            tMaxXLT += scaleX
#            tMaxYLT += scaleY
#            if xIndex == 0:
#                tMinXLT -= scaleX
#            if yIndex == 0:
#                tMinYLT -= scaleY
             
            tName = ('tile_%d_%d') % (int(tMinX), int(tMinY))
            tiles.append((tName, tMinXLT, tMinYLT, tMaxXLT, tMaxYLT, box(tMinXGeos, tMinYGeos, tMaxXGeos, tMaxYGeos)))
            executeCommand('mkdir -p ' + outputFolder + '/' + tName)

    # Process the input files
    # For each file we check which tiles it overlaps:
    #   - If it is completely inside a tile we copy the file to the output folder of the tile
    #   - If it is partially overlapping many tiles, we run lasmerge to cut the file into the pieces that need to go to each tile folder
    for i in range(numInputFiles):
        inputFile = inputFiles[i]
        (_, _, minX, minY, _, maxX, maxY, _, _, _, _, _, _, _) = lasops.getPCFileDetails(inputFile)
        geom = box(minX, minY, maxX, maxY)
        print (i+1), numInputFiles, os.path.basename(inputFile), minX, minY, maxX, maxY
        for (tName, tMinX, tMinY, tMaxX, tMaxY, tBox) in tiles:
            relation = _relation(tBox, geom)
            if relation == 1:
                executeCommand('cp ' + inputFile + ' ' + outputFolder + '/' + tName)
                break # If it is completely inside one tile, we do not need to check the rest
            elif relation == 2:
                executeCommand('lasmerge -i ' + inputFile + ' -inside ' + str(tMinX) + ' ' + str(tMinY) + ' ' + str(tMaxX) + ' ' + str(tMaxY) + ' -o ' + outputFolder + '/' + tName + '/cut_' + os.path.basename(inputFile))
#                executeCommand('las2las -i ' + inputFile + ' -keep_xy ' + str(tMinX) + ' ' + str(tMinY) + ' ' + str(tMaxX) + ' ' + str(tMaxY) + ' -o ' + outputFolder + '/' + tName + '/cut_' + os.path.basename(inputFile))
            
    # Check that the number of points after tiling is the same as initial
    numPointsTiles = 0
    numFilesTiles = 0
    for (tName, _, _, _, _, _) in tiles:
        (tInputFiles, _, tNumPoints, _, _, _, _, _, _, _, _, _) = lasops.getPCFolderDetails(outputFolder + '/' + tName)
        numPointsTiles += tNumPoints
        numFilesTiles += len(tInputFiles)
        
    if numPointsTiles != numPoints:
        print 'Warning: #input_points = %d   #output_points = %d' % (numPoints, numPointsTiles)
    else:
        print '#input_points = #output_points = %d' % numPointsTiles
    print '#input_files = %d   #output_files = %d' % (numInputFiles, numFilesTiles)
    
if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output folder: ', args.output
    print 'Number of tiles: ', args.number
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output, args.number)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
