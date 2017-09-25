#!/usr/bin/env python

"""Gets the CAABB, number of points and average density for a point cloud. Also gets a suggested potreeconverter command"""

import argparse, traceback, sys, math, time, os
from pympc import utils

def run(inputFolder, numberProcs, targetTile, targetSize):
    (_, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, _, _, _) = utils.getPCFolderDetails(inputFolder, numberProcs)
    #convert to integers
    tminx = int(math.ceil(tminx))
    tminy = int(math.ceil(tminy))
    tminz = int(math.ceil(tminz))
    tmaxx = int(math.floor(tmaxx))
    tmaxy = int(math.floor(tmaxy))
    tmaxz = int(math.floor(tmaxz))

    tRangeX = tmaxx - tminx
    tRangeY = tmaxy - tminy
    tRangeZ = tmaxz - tminz

    density2  = float(tcount) / (tRangeX*tRangeY)
    #density3  = float(tcount) / (tRangeX*tRangeY*tRangeZ)

    maxRange = max((tRangeX, tRangeY, tRangeZ))

    (minX,minY,minZ,maxX,maxY,maxZ) = (tminx, tminy, tminz, tminx + maxRange, tminy + maxRange, tminz + maxRange)

    print('AABB: ', tminx, tminy, tminz, tmaxx, tmaxy, tmaxz)
    print('#Points:' , tcount)
    print('Average density [pts / m2]:' , density2)
    #print('Average density [pts / m3]:' , density3)

    if tcount < targetTile:
        print('Suggested number of tiles: 1. For this number of points Massive-PotreeConverter is not really required!')
    else:
        c = 1
        numpertile = None
        while True:
            numtiles = math.pow(math.pow(2,c),2)
            numpertile = float(tcount) / numtiles
            if numpertile < targetTile:
                break
            else:
                c+=1
        print('Suggested number of tiles: ', numtiles)

    deepSpacing = 1 / math.sqrt(density2)
    spacing = math.ceil(maxRange / math.sqrt(targetSize))

    numlevels = 0
    lspacing = spacing
    while lspacing > deepSpacing:
        numlevels+=1
        lspacing = lspacing / 2
    numlevels+=1

    print('Suggested Potree-OctTree CAABB: ', minX,minY,minZ,maxX,maxY,maxZ)
    print('Suggested Potree-OctTree spacing: ', spacing)
    print('Suggested Potree-OctTree number of levels: ', numlevels)
    print('Suggested potreeconverter command:')
    print('$(which PotreeConverter) -o <potree output directory> -l %i -s %i --CAABB "%i %i %i %i %i %i" --output-format LAZ -i <laz input directory>' % (numlevels, spacing, minX,minY,minZ,maxX,maxY,maxZ))

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Gets the bounding box of the points in the files of the input folder. Also computes the number of points and the density. It also suggests spacing and number of levels to use for PotreeConverter")
    parser.add_argument('-i','--input',default='',help='Input folder with the point cloud files',type=str, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    parser.add_argument('-m','--avgtile',default=5000000000,help='Target average number of points per tile [default is 5000000000]',type=int)
    parser.add_argument('-t','--avgnode',default=60000,help='Target average number of points per OctTree node [default is 60000]',type=int)
    return parser

def main():
    args = argument_parser().parse_args()
    print('Input folder: ' , args.input)
    print('Number of processes: ' , args.proc)
    print('Target tile number of points: ' , args.avgtile)
    print('Target OctTree node number of points: ' , args.avgnode)
    
    try:
        t0 = time.time()
        print('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.proc, args.avgtile, args.avgnode)
        print('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print('Execution failed!')
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
