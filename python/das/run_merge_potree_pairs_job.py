#!/usr/bin/env python
import os,sys,multiprocessing

# Merges pairs of potree octrees. If 8 tiles are given this will produce 4 merged ones. For each merge process:
# The data is copied from a shared folder (between the nodes in a cluster) to a local folder
# The merging is done locally
# The merged data is copied back to the shared folder
# Remove local copies
# The different parallel processes are delayed in order to avoid simult. IO  

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
    os.system('mkdir -p ' + outputFolder)

    os.system('source ' + setEnvAbsPath + '; merge_potree.py -a ' + tileALocalInputFolder + ' -b ' + tileBLocalInputFolder + ' -o ' + tileOLocalOutputFolder + ' -m  &> ' + tileOOutputFolder + '.log')

    os.system('cp -r ' + tileOLocalOutputFolder + ' ' + outputFolder)

    os.system('rm -rf ' + tileALocalInputFolder)
    os.system('rm -rf ' + tileBLocalInputFolder)
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

if len(tiles) % 2:
   #An odd number means that the last tile can be directly copied to the output folder
   os.system('cp -r ' + inputFolder + '/' + tiles[-1] + ' ' + outputFolder + '/' + tiles[-1] )

for i in range(numtasks):
    jobs[i].join()

print 'Done!'
