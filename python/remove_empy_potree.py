import os, sys

inputAbsPath = os.path.abspath(sys.argv[1])

for e in os.listdir(inputAbsPath):
    eAbsPath = inputAbsPath + '/' + e
    if os.path.isdir(eAbsPath):
        eDataAbsPath = eAbsPath + '/data'
        if os.path.isdir(eDataAbsPath) and len(os.listdir(eDataAbsPath)):
            print e + ' is ok'
        else:
            print e + ' is ko'
            os.system('rm -rf ' + eAbsPath + '*')
