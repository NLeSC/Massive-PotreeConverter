#!/usr/bin/env python
import os,sys,numpy

# Create qsub tasks for merging all the provided potree octrees

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
runJobAbsPath = sys.argv[5]
setEnvAbsPath = sys.argv[6]

print 'qsub -l h_rt=99:00:00 -V -N pmerge ' + runJobAbsPath + ' ' + inputFolder + ' ' + outputFolder + ' ' + localInputFolder + ' ' + localOutputFolder + ' ' + setEnvAbsPath 

