#!/usr/bin/env python
import os,sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
setEnvAbsPath = sys.argv[3]
tiles = sys.argv[4].split(',')

validTiles = []
for tile in tiles:
    dataAbsPath = inputFolder + '/' + tile + '/data'
    if os.path.isdir(dataAbsPath) and len(os.listdir(dataAbsPath)):
        validTiles.append(tile)

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
    os.system('source ' + setEnvAbsPath + '; merge_potree.py -a ' + tileAInputFolder + ' -b ' + tileBInputFolder + ' -o ' + tileOOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log')

print 'Done!'
