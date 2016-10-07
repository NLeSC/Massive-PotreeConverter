#!/usr/bin/env python
"""Merge two Potree OctTrees into a single one."""

import argparse, traceback, time, os, json, numpy
from pympc import utils


def fixHeader(inputFile, outputFile):
    (_, minX, minY, minZ, maxX, maxY, maxZ, _, _, _, _, _, _) = utils.getPCFileDetails(inputFile)
    utils.shellExecute('lasinfo -i %s -nc -nv -nco -set_bounding_box %f %f %f %f %f %f' % (outputFile, minX, minY, minZ, maxX, maxY, maxZ))


def joinNode(node, nodeAbsPathA, nodeAbsPathB, nodeAbsPathO, hierarchyStepSize, extension, cmcommand):
    hrcFile = node + '.hrc'
    hrcA = None
    if os.path.isfile(nodeAbsPathA + '/' + hrcFile):
        # Check if there is data in this node in Octtree A (we check if the HRC file for this node exist)
        hrcA = utils.readHRC(nodeAbsPathA + '/' + hrcFile, hierarchyStepSize)
        if len(os.listdir(nodeAbsPathA)) == 2:
            hrcA[0][0] = utils.getPCFileDetails(nodeAbsPathA + '/' + node + extension)[0]
    hrcB = None
    if os.path.isfile(nodeAbsPathB + '/' + hrcFile):
        # Check if there is data in this node in Octtree B (we check if the HRC file for this node exist)
        hrcB = utils.readHRC(nodeAbsPathB + '/' + hrcFile, hierarchyStepSize)
        if len(os.listdir(nodeAbsPathB)) == 2:
            hrcB[0][0] = utils.getPCFileDetails(nodeAbsPathB + '/' + node + extension)[0]

    if hrcA != None and hrcB != None:
        utils.shellExecute('mkdir -p ' + nodeAbsPathO)
        # If both Octtrees A and B have data in this node we have to merge them
        hrcO = utils.initHRC(hierarchyStepSize)
        for level in range(hierarchyStepSize+2):
            numChildrenA = len(hrcA[level])
            numChildrenB = len(hrcB[level])
            numChildrenO = max((numChildrenA, numChildrenB))
            if level < (hierarchyStepSize+1):
                for i in range(numChildrenO):
                    hasNodeA = (i < numChildrenA) and (hrcA[level][i] > 0)
                    hasNodeB = (i < numChildrenB) and (hrcB[level][i] > 0)
                    (childNode, isFile) = utils.getNodeName(level, i, node, hierarchyStepSize, extension)
                    if hasNodeA and hasNodeB:
                        hrcO[level].append(hrcA[level][i] + hrcB[level][i])
                        #merge lAZ or folder (iteratively)
                        if isFile:
                            utils.shellExecute('lasmerge -i ' +  nodeAbsPathA + '/' + childNode + ' ' +  nodeAbsPathB + '/' + childNode + ' -o ' + nodeAbsPathO + '/' + childNode)
                            #We now need to set the header of the output file as the input files (lasmerge will have shrink it and we do not want that
                            fixHeader(nodeAbsPathA + '/' + childNode, nodeAbsPathO + '/' + childNode)
                        else:
                            joinNode(node + childNode, nodeAbsPathA + '/' + childNode, nodeAbsPathB + '/' + childNode, nodeAbsPathO + '/' + childNode, hierarchyStepSize, extension, cmcommand)
                    elif hasNodeA:
                        #mv / cp
                        hrcO[level].append(hrcA[level][i])
                        utils.shellExecute(cmcommand + nodeAbsPathA + '/' + childNode + ' ' + nodeAbsPathO + '/' + childNode)
                    elif hasNodeB:
                        #mv / cp
                        hrcO[level].append(hrcB[level][i])
                        utils.shellExecute(cmcommand + nodeAbsPathB + '/' + childNode + ' ' + nodeAbsPathO + '/' + childNode)
                    else:
                        hrcO[level].append(0)
            else:
                hrcO[level] = list(numpy.array(hrcA[level] + ([0]*(numChildrenO - numChildrenA))) + numpy.array(hrcB[level] + ([0]*(numChildrenO - numChildrenB))))
        # Write the HRC file
        utils.writeHRC(nodeAbsPathO + '/' + hrcFile, hierarchyStepSize, hrcO)
    elif hrcA != None:
        # Only Octtree A has data in this node. We can directly copy it to the output Octtree
        utils.shellExecute(cmcommand + nodeAbsPathA + ' ' + nodeAbsPathO)
    elif hrcB != None:
        # Only Octtree B has data in this node. We can directly copy it to the output Octtree
        utils.shellExecute(cmcommand + nodeAbsPathB + ' ' + nodeAbsPathO)

def createCloudJS(cloudJSA, cloudJSB, cloudJSO):
    result = False # Is the data properly merged

    cloudJSDataA = json.loads(open(cloudJSA, 'r').read())
    cloudJSDataB = json.loads(open(cloudJSB, 'r').read())

    cloudJSDataO = {}
    # Compare fields in the input cloud.js's that should be equal
    # We also write the fields in the output cloud.js
    for equalField in ["version", "octreeDir", "boundingBox", "pointAttributes", "spacing", "scale", "hierarchyStepSize"]:
        if cloudJSDataA[equalField] == cloudJSDataB[equalField]:
             cloudJSDataO[equalField] = cloudJSDataA[equalField]
        else:
            raise Exception('Error: Can not join cloud.js. Distinct ' + equalField + '!')

    # For the field "tightBoundingBox" we need to merge them since they can be different
    tbbA = cloudJSDataA["tightBoundingBox"]
    tbbB = cloudJSDataB["tightBoundingBox"]

    tbbO = {}
    tbbO["lx"] = min([tbbA["lx"], tbbB["lx"]])
    tbbO["ly"] = min([tbbA["ly"], tbbB["ly"]])
    tbbO["lz"] = min([tbbA["lz"], tbbB["lz"]])
    tbbO["ux"] = max([tbbA["ux"], tbbB["ux"]])
    tbbO["uy"] = max([tbbA["uy"], tbbB["uy"]])
    tbbO["uz"] = max([tbbA["uz"], tbbB["uz"]])
    cloudJSDataO["tightBoundingBox"] = tbbO

    hierarchyStepSize = cloudJSDataA['hierarchyStepSize']

    cloudJSOFile = open(cloudJSO, 'w')
    cloudJSOFile.write(json.dumps(cloudJSDataO, indent=4))
    cloudJSOFile.close()

    return hierarchyStepSize

def run(inputFolderA, inputFolderB, outputFolder, moveFiles):
    # Check input parameters
    if (not os.path.isdir(inputFolderA)) or (not os.path.isdir(inputFolderB)):
        raise Exception('Error: Some of the input folder does not exist!')
    if os.path.isfile(outputFolder):
        raise Exception('Error: There is a file with the same name as the output folder. Please, delete it!')
    elif os.path.isdir(outputFolder) and os.listdir(outputFolder):
        raise Exception('Error: Output folder exists and it is not empty. Please, delete the data in the output folder!')

    # Make the paths absolute path
    inputFolderA = os.path.abspath(inputFolderA)
    inputFolderB = os.path.abspath(inputFolderB)
    outputFolder = os.path.abspath(outputFolder)

    if moveFiles:
        cmcommand = 'mv '
    else:
        cmcommand = 'cp -r '

    dataA = inputFolderA + '/data'
    dataB = inputFolderB + '/data'
    dataO = outputFolder + '/data'

    # Check if the octtrees have actual data (i.e. one folder with the root node)
    hasNodeA = os.listdir(dataA) == ['r',]
    hasNodeB = os.listdir(dataB) == ['r',]

    if hasNodeA or hasNodeB:
        utils.shellExecute('mkdir -p ' + outputFolder)
        if hasNodeA and hasNodeB:
            # If both Octrees have data we need to merge them
            # Create output cloud.js from joining the two input ones
            cloudJSA = inputFolderA + '/cloud.js'
            cloudJSB = inputFolderB + '/cloud.js'
            if not (os.path.isfile(cloudJSA)) or not (os.path.isfile(cloudJSB)):
                raise Exception('Error: Some cloud.js is missing!')
            # We also get the hierarchyStepSize
            hierarchyStepSize = createCloudJS(cloudJSA, cloudJSB, outputFolder + '/cloud.js')
            listFileRootA =  os.listdir(dataA + '/r')
            if 'r.las' in listFileRootA:
                extension = 'las'
            elif 'r.laz' in listFileRootA:
                extension = 'laz'
            else:
                raise Exception('Error: ' + __file__ + ' only compatible with las/laz format')
            joinNode('r', dataA + '/r', dataB + '/r', dataO + '/r', hierarchyStepSize, extension, cmcommand)
        elif hasA:
            utils.shellExecute(cmcommand + inputFolderA + '/* ' + outputFolder)
        else:
            utils.shellExecute(cmcommand + inputFolderB + '/* ' + outputFolder)
    else:
        print ('Nothing to merge: both Octtrees are empty!')

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="Merge two Potree OctTrees into a single one")
    parser.add_argument('-a','--inputa',default='',help='Input Potree-OctTree A',type=str, required=True)
    parser.add_argument('-b','--inputb',default='',help='Input Potree-OctTree B',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output Potree-OctTree',type=str, required=True)
    parser.add_argument('-m','--move',help='Use mv instead of cp when merging Potree-OctTrees. In this case the input data is partially dropped (but process will be faster due to less required IO) [default False]',default=False,action='store_true')
    return parser

def main():
    args = argument_parser().parse_args()
    print ('Input Potree Octtree A: ', args.inputa)
    print ('Input Potree Octtree B: ', args.inputb)
    print ('Output Potree Octtree: ', args.output)
    print ('Move: ', args.move)

    try:
        t0 = time.time()
        print ('Starting ' + os.path.basename(__file__) + '...')
        run(args.inputa, args.inputb, args.output, args.move)
        print ('Finished in %.2f seconds' % (time.time() - t0))
    except:
        print ('Execution failed!')
        print (traceback.format_exc())

if __name__ == "__main__":
    main()
