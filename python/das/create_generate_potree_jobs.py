#!/usr/bin/env python
import os,sys,numpy

# Create the qsub tasks for generating potree octtrees

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
runJobAbsPath = sys.argv[5]
setEnvAbsPath = sys.argv[6]
num = int(sys.argv[7])

tilesList = sorted(os.listdir(inputFolder))
for tilesSubList in numpy.array_split(tilesList, len(tilesList)/(num-1)):
    print 'qsub -l h_rt=99:00:00 -V -N potree ' + runJobAbsPath + ' ' + inputFolder + ' ' + outputFolder + ' ' + localInputFolder + ' ' + localOutputFolder + ' ' + setEnvAbsPath + ' ' + ','.join(tilesSubList) 

