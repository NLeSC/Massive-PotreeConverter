#!/usr/bin/env python
import os,sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
setEnvAbsPath = sys.argv[5]

os.system('rm -rf ' + localInputFolder)
os.system('rm -rf ' + localOutputFolder)
os.system('mkdir -p ' + os.path.basename(localInputFolder))
os.system('mkdir -p ' + os.path.basename(localOutputFolder))
os.system('cp -r ' + inputFolder +  ' ' + localInputFolder)
os.system('mkdir -p ' + os.path.basename(outputFolder))

os.system('source ' + setEnvAbsPath + '; merge_potree_all.py -i ' + localInputFolder + ' -o ' + localOutputFolder)

os.system('cp -r ' + localOutputFolder + ' ' + outputFolder)

os.system('rm -rf ' + localInputFolder)
os.system('rm -rf ' + localOutputFolder)

print 'Done!'
