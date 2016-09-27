#!/usr/bin/env python
"""Gets the CAABB, number of points and average density for a point cloud"""

import argparse, traceback, sys, math, time, os
import utils

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create the Octtrees of each tile of the input data folder")
    parser.add_argument('-i','--input',default='',help='Input folder with the point cloud files',type=str, required=True)
    parser.add_argument('-c','--proc',default=1,help='Number of processes [default is 1]',type=int)
    return parser

def run(inputFolder, numberProcs):
    (_, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, _, _, _) = utils.getPCFolderDetails(inputFolder, numberProcs)
    #convert to integers
    tminx = int(math.ceil(tminx))
    tminy = int(math.ceil(tminy))
    tminz = int(math.ceil(tminz))
    tmaxx = int(math.floor(tmaxx))
    tmaxy = int(math.floor(tmaxy))
    tmaxz = int(math.floor(tmaxz))
    maxRange = max((tmaxx - tminx, tmaxy - tminy, tmaxz - tminz))
    (minX,minY,minZ,maxX,maxY,maxZ) = (tminx, tminy, tminz, tminx + maxRange, tminy + maxRange, tminz + maxRange)
    density  = float(tcount) / ((tmaxx - tminx)*(tmaxy - tminy)*(tmaxz - tminz))
    print 'CAABB:', minX,minY,minZ,maxX,maxY,maxZ
    print '#Points:', tcount
    print 'Average density:', density


if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Number of processes: ', args.proc
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.proc)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()