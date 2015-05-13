#!/usr/bin/env python
"""This script generate for each tile a WKT with BBOX of the contained files"""
import os, argparse, traceback, time
from pointcloud import lasops

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create WKT with extents of files in the tiles")
    parser.add_argument('-i','--input',default='',help='Input folder with the tiles',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output folder to dump the WKT files',type=str, required=True)
    return parser

def run(inputFolder, outputFolder):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')  
    
    os.system('mkdir -p ' + outputFolder)
    for tile in os.listdir(inputFolder):
        tFile = open(outputFolder + '/' + tile + '.wkt', 'w')
        for tilefile in os.listdir(inputFolder + '/' + tile):
            (_, _, fMinX, fMinY, _, fMaxX, fMaxY, _, _, _, _, _, _, _) = lasops.getPCFileDetails(inputFolder + '/' + tile + '/' + tilefile)
            tFile.write('POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))\n' % (fMinX, fMaxY, fMinX, fMinY, fMaxX, fMinY, fMaxX, fMaxY, fMinX, fMaxY))
        tFile.close()

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output folder: ', args.output
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()

