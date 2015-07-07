#!/usr/bin/env python
import os,sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
setEnvAbsPath = sys.argv[5]

def run_command(c):
    print c
    os.system(c)

run_command('rm -rf ' + localInputFolder)
run_command('rm -rf ' + localOutputFolder)
run_command('mkdir -p ' + os.path.dirname(os.path.abspath(localInputFolder)))
run_command('mkdir -p ' + os.path.dirname(os.path.abspath(localOutputFolder)))
run_command('cp -r ' + inputFolder +  ' ' + localInputFolder)
run_command('mkdir -p ' + os.path.dirname(os.path.abspath(outputFolder)))

run_command('source ' + setEnvAbsPath + '; merge_potree_all.py -i ' + localInputFolder + ' -o ' + localOutputFolder)

run_command('cp -r ' + localOutputFolder + ' ' + outputFolder)

run_command('rm -rf ' + localInputFolder)
run_command('rm -rf ' + localOutputFolder)

print 'Done!'
