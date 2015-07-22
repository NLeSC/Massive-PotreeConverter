#!/usr/bin/env python
import os,sys,multiprocessing

# Runs in parallel the generation of the given tiles. For each tile:
# It copies it from inputFolder (shared by all cluster nodes) to a local folder
# Process it
# Copies the result to the shared folder
# Remove local copies
# The different parallel processes are delayed in order to avoid simult. IO

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]
localInputFolder = sys.argv[3]
localOutputFolder = sys.argv[4]
setEnvAbsPath = sys.argv[5]
tiles = sys.argv[6].split(',')

def worker(tile, sleepTime):
    os.system('sleep ' + str(sleepTime))

    tileLocalInputFolder = localInputFolder + '/' + tile
    tileLocalOutputFolder = localOutputFolder + '/' + tile
    tileInputFolder = inputFolder + '/' + tile
    tileOutputFolder = outputFolder + '/' + tile 

    os.system('rm -rf ' + tileOutputFolder)
    os.system('cp -r ' + tileInputFolder +  ' ' + tileLocalInputFolder)
    os.system('mkdir -p ' + tileLocalOutputFolder)
    os.system('mkdir -p ' + outputFolder)

    os.system('source ' + setEnvAbsPath + '; PotreeConverter --outdir ' + tileLocalOutputFolder + ' --levels 13 --output-format LAZ --source ' + tileLocalInputFolder + ' --spacing 1024 --aabb "13420.00 306740.00 -30.00 278490.00 615440.00 400.00" &> ' + tileOutputFolder + '.log')

    os.system('cp -r ' + tileLocalOutputFolder + ' ' + outputFolder)

    os.system('rm -rf ' + tileLocalInputFolder)
    os.system('rm -rf ' + tileLocalOutputFolder)
    return

numtiles = len(tiles)
os.system('mkdir -p ' + localInputFolder)
os.system('mkdir -p ' + localOutputFolder)
jobs = []
for i in range(numtiles):
    p = multiprocessing.Process(target=worker, args=(tiles[i],100*i))
    jobs.append(p)
    p.start()

for i in range(numtiles):
    jobs[i].join()

print 'Done!'
