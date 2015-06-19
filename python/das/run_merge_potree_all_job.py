#!/usr/bin/env python
import os,sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
setEnvAbsPath = sys.argv[3]
tiles = sys.argv[4].split(',')

for mIndex in range(1, len(tiles)):
    if mIndex == 1:
        tileAInputFolder = inputFolder + '/' + tiles[0]
    else:
        tileAInputFolder = tileOOutputFolder + '/' + 'tile_merged_%d' % (mIndex-1)
    tileBInputFolder = inputFolder + '/' + tiles[mIndex]
    
    tileO = 'tile_merged_%d' % mIndex
    tileOOutputFolder = outputFolder + '/' + tileO
    
    if os.path.isdir(tileOOutputFolder):
        raise Exception(tileOOutputFolder + ' already exists!')
    
    os.system('mkdir -p ' + tileOOutputFolder)
    os.system('source ' + setEnvAbsPath + '; merge_potree.py -a ' + tileAInputFolder + ' -b ' + tileBInputFolder + ' -o ' + tileOOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log')

print 'Done!'
