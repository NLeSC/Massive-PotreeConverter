#!/usr/bin/env python
import os,sys,numpy

# Create qsub tasks for merging all the provided potree octrees

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
runJobAbsPath = sys.argv[2]
setEnvAbsPath = sys.argv[4]
num = int(sys.argv[7])

tilesList = sorted(os.listdir(inputFolder))

print 'qsub -l h_rt=99:00:00 -V -N potree ' + runJobAbsPath + ' ' + inputFolder + ' ' + outputFolder + ' ' + setEnvAbsPath + ' ' + ','.join(tilesList) 

