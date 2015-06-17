#!/usr/bin/env python
import os,sys,multiprocessing

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
setEnvAbsPath = sys.argv[5]
tiles = sys.argv[6].split(',')

def worker(tileA, tileB, sleepTime):
    os.system('sleep ' + str(sleepTime))
    tileO = tileA + '_' + tileB
    tileALocalInputFolder = localInputFolder + '/' + tileA
    tileBLocalInputFolder = localInputFolder + '/' + tileB
    tileOLocalOutputFolder = localOutputFolder + '/' + tileO
    tileAInputFolder = inputFolder + '/' + tileA
    tileBInputFolder = inputFolder + '/' + tileB
    tileOOutputFolder = outputFolder + '/' + tileO 

    os.system('rm -rf ' + tileOOutputFolder)
    os.system('cp -r ' + tileAInputFolder +  ' ' + tileALocalInputFolder)
    os.system('cp -r ' + tileBInputFolder +  ' ' + tileBLocalInputFolder)
    os.system('mkdir -p ' + tileOLocalOutputFolder)
    os.system('mkdir -p ' + tileOOutputFolder)

    os.system('source ' + setEnvAbsPath + '; merge_potree.py -a ' + tileALocalInputFolder + ' -b ' + tileBLocalInputFolder + ' -o ' + tileOLocalOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log')

    os.system('cp -r ' + tileOLocalOutputFolder + ' ' + tileOOutputFolder)

    os.system('rm -rf ' + tileOLocalInputFolder)
    os.system('rm -rf ' + tileOLocalOutputFolder)
    return

os.system('mkdir -p ' + localInputFolder)
os.system('mkdir -p ' + localOutputFolder)
jobs = []
numtasks = len(tiles) / 2
for i in range(numtasks):
    p = multiprocessing.Process(target=worker, args=(tiles[2*i], tiles[(2*i) + 1],100*i))
    jobs.append(p)
    p.start()

for i in range(numtasks):
    jobs[i].join()

print 'Done!'
