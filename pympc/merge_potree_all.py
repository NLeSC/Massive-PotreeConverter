#!/usr/bin/env python
import os, sys, time, argparse, traceback
from pympc import utils
from pympc import merge_potree

def run(inputFolder, outputFolder, moveFiles):

    # List the elements in the input folder
    inputOctTrees = os.listdir(inputFolder)
    # Consider as valid Octrees the folder that have a data subdirectory
    validInputOctTrees = []
    for inputOctTree in inputOctTrees:
        dataAbsPath = inputFolder + '/' + inputOctTree + '/data'
        if os.path.isdir(dataAbsPath) and len(os.listdir(dataAbsPath)):
            validInputOctTrees.append(inputOctTree)
        else:
            print ('Ignoring ' + inputOctTree)
    print (','.join(validInputOctTrees))

    stdout = sys.stdout
    stderr = sys.stderr
    octTreeOutputFolder = None
    for mIndex in range(1, len(validInputOctTrees)):
        if mIndex == 1:
            octTreeAInputFolder = inputFolder + '/' + validInputOctTrees[0]
        else:
            octTreeAInputFolder = outputFolder + '/' + 'merged_%d' % (mIndex-1)
        octTreeBInputFolder = inputFolder + '/' + validInputOctTrees[mIndex]

        octTreeOutputFolder = outputFolder + '/' + 'merged_%d' % mIndex

        if os.path.isdir(octTreeOutputFolder):
            raise Exception(octTreeOutputFolder + ' already exists!')

        os.system('mkdir -p ' + octTreeOutputFolder)
        ofile = open(octTreeOutputFolder + '.log', 'w')
        efile = open(octTreeOutputFolder + '.err', 'w')
        sys.stdout = ofile
        sys.stderr = efile
        print ('Input Potree Octtree A: ', octTreeAInputFolder)
        print ('Input Potree Octtree B: ', octTreeBInputFolder)
        print ('Output Potree Octtree: ', octTreeOutputFolder)
        t0 = time.time()
        merge_potree.run(octTreeAInputFolder, octTreeBInputFolder, octTreeOutputFolder, moveFiles)
        print ('Finished in %.2f seconds' % (time.time() - t0))
        ofile.close()
        efile.close()
        sys.stdout = stdout
        sys.stderr = stderr
    print("Final merged Potree-OctTree is in ", octTreeOutputFolder)

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Merge all Potree-OctTrees in the input folder into a single one")
    parser.add_argument('-i','--input',default='',help='Input folder with different Potree-OctTrees',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output/Execution folder for the various merging processes. The final merged Potree-OctTree will be a folder called merged_X with X the highest value',type=str, required=True)
    parser.add_argument('-m','--move',help='Use mv instead of cp when merging Potree-OctTrees. In this case the input data is partially dropped (but process will be faster due to less required IO) [default False]',default=False,action='store_true')
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input folder with Potree-OctTrees: ', args.input)
    print ('Output Potree OctTree: ', args.output)
    print ('Move: ', args.move)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.input, args.output, args.move)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
