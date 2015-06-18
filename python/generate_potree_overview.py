#!/usr/bin/env python
"""Create a the overview Octtree from the Octtree data of the tiles"""
import argparse, traceback, time, os
import utils

# Check that PotreeConverter with extension to specify the AABB is installed
if utils.shellExecute('PotreeConverter -h').count('usage: ') == 0:
    raise Exception("PotreeConverter is not installed")

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Create a the overview Octtree from the Octtree data of the tiles")
    parser.add_argument('-i','--input',default='',help='Input folder with the Potree data of the tiles',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output folder for the Potree data for the overview',type=str, required=True)
    parser.add_argument('-t','--temp',default='',help='Temporal folder where required processing is done',type=str, required=True)
    parser.add_argument('-l','--ilevels',default='',help='Maximum level to be used from the tiles OctTrees',type=int, required=True)
    parser.add_argument('-f','--format',default='',help='Format (LAS or LAZ)',type=str, required=True)
    parser.add_argument('-e','--olevels',default='',help='Number of levels for the overview OctTree',type=int, required=True)
    parser.add_argument('-s','--spacing',default='',help='Spacing at root level',type=int, required=True)
    return parser

def run(inputFolder, outputFolder, tempFolder, iLevels, format, oLevels, spacing):
    # Check input parameters
    if not os.path.isdir(inputFolder):
        raise Exception('Error: Input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')
    
    if iLevels > 4:
        raise Exception('Error: iLevels must be < 5!')
    
    # Make it absolute path
    inputFolder = os.path.abspath(inputFolder)

    os.system('mkdir -p ' + outputFolder)
    os.system('mkdir -p ' + tempFolder)
    
    tilesNames = os.listdir(inputFolder)
    numTiles = len(tilesNames)
    
    # We add links to the files with level lower than indeicated
    for i in range(numTiles):
        dataAbsPath = inputFolder + '/' + tilesNames[i] + '/data/r'
        if os.path.isdir(dataAbsPath):
            for f in os.listdir(dataAbsPath):
                if 'la' in f and ((len(f) - 5) <= iLevels):
                    os.system('ln -s ' + dataAbsPath + '/' + f + ' ' + tempFolder + '/' + tilesNames[i] + '_' + f)
    
    c = 'PotreeConverter -o ' + outputFolder +  ' -l ' + str(oLevels) + ' --output-format ' + str(format).upper() + ' --source ' + tempFolder + ' -s ' + str(spacing) + ' &> ' + outputFolder + '.log'
    print c
    os.system(c)

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output folder: ', args.output
    print 'Temporal folder: ', args.temp
    print 'Levels from Input: ', args.ilevels
    print 'Format: ', args.format
    print 'Output Levels: ', args.olevels
    print 'Spacing: ', args.spacing
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output, args.temp, args.ilevels, args.format, args.olevels, args.spacing)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
