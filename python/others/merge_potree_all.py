#!/usr/bin/env python
import os,sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
tiles = os.listdir(inputFolder)

validTiles = []
for tile in tiles:
    dataAbsPath = inputFolder + '/' + tile + '/data'
    if os.path.isdir(dataAbsPath) and len(os.listdir(dataAbsPath)):
        validTiles.append(tile)
    else:
        print 'Ignoring ' + tile

print ','.join(validTiles)

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
    command = 'python /home/oscar/sw/Massive-PotreeConverter/python/merge_potree.py -a ' + tileAInputFolder + ' -b ' + tileBInputFolder + ' -o ' + tileOOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log'
    print command
    os.system(command)

print 'Done!'
