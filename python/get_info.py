import utils
import sys
import math

absPath = sys.argv[1]
numProc = sys.argv[2] #number of processes to use for reading the input path
(_, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, _, _, _) = utils.getPCFolderDetails(absPath, numProc)
#convert to integers
tminx = int(math.ceil(tminx))
tminy = int(math.ceil(tminy))
tminz = int(math.ceil(tminz))
tmaxx = int(math.floor(tmaxx))
tmaxy = int(math.floor(tmaxy))
tmaxz = int(math.floor(tmaxz))
maxRange = max((tmaxx - tminx, tmaxy - tminy, tmaxz - tminz))
(minX,minY,minZ,maxX,maxY,maxZ) = (tminx, tminy, tminz, tminx + maxRange, tminy + maxRange, tminz + maxRange)
density  = float(tcount) / ((tmaxx - tminx)*(tmaxy - tminy)*(tmaxz - tminz))
print 'CAABB:', minX,minY,minZ,maxX,maxY,maxZ
print '#Points:', tcount
print 'Average density:', density