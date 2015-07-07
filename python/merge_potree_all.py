#!/usr/bin/env python
import os, sys, time
import merge_potree, utils

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
tiles = os.listdir(inputFolder)

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Merge all Potree OctTrees in the input folder into a single one")
    parser.add_argument('-i','--input',default='',help='Input folder with different Potree Octtrees',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output Potree OctTree',type=str, required=True)
    return parser


validTiles = []
for tile in tiles:
    dataAbsPath = inputFolder + '/' + tile + '/data'
    if os.path.isdir(dataAbsPath) and len(os.listdir(dataAbsPath)):
        validTiles.append(tile)
    else:
        print 'Ignoring ' + tile

print ','.join(validTiles)

stdout = sys.stdout
stderr = sys.stderr

for mIndex in range(1, len(validTiles)):
    if mIndex == 1:
        tileAInputFolder = inputFolder + '/' + validTiles[0]
    else:
        tileAInputFolder = outputFolder + '/' + 'tile_merged_%d' % (mIndex-1)
    tileBInputFolder = inputFolder + '/' + validTiles[mIndex]
    
    tileOOutputFolder = outputFolder + '/' + 'tile_merged_%d' % mIndex
    
    if os.path.isdir(tileOOutputFolder):
        raise Exception(tileOOutputFolder + ' already exists!')
    
    os.system('mkdir -p ' + tileOOutputFolder)
    sys.stdout = open(tileOOutputFolder + '.log', 'w')
    sys.stderr = open(tileOOutputFolder + '.err', 'w')
    print 'Input Potree Octtree A: ', tileAInputFolder
    print 'Input Potree Octtree B: ', tileBInputFolder
    print 'Output Potree Octtree: ', tileOOutputFolder
    merge_potree.run(tileAInputFolder, tileBInputFolder, tileOOutputFolder, True)
    sys.stdout = stdout
    sys.stderr = std.err
    #command = 'python /home/oscar/sw/Massive-PotreeConverter/python/merge_potree.py -a ' + tileAInputFolder + ' -b ' + tileBInputFolder + ' -o ' + tileOOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log'
    #print command
    #os.system(command)
    
if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Input folder with Potree Octtrees: ', args.input
    print 'Output Potree Octtree: ', args.output
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.input, args.output)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
