#!/usr/bin/python
import argparse
from lxml import etree

def run(inputFolder, outputFile, outputFormat, levels, spacing, extent):
    # Check user parameters
    if not os.path.isdir(inputFolder):
        raise Exception(inputFolder + ' does not exist')
    if os.path.isfile(outputFile):
        raise Exception(outputFile + ' already exists!')
    outputFileAbsPath = os.path.abspath(outputFile)

    # Create output file
    oFile = open(outputFileAbsPath, 'w')
    xmlRootElement = etree.Element('ParCommands')

    for tile in os.listdir(inputFolder):
        tileRelPath = inputFolder + '/' + tile

        xmlComponentElement = etree.SubElement(xmlRootElement, 'Component')

        xmlIdElement = etree.SubElement(xmlComponentElement, 'id')
        xmlIdElement.text = tile + '_potree_converter'

        xmlRequireElement = etree.SubElement(xmlRootElement, 'require')
        xmlRequireElement.text = tileRelPath

        localOutputFolder = tile + '_potree'

        xmlCommandElement = etree.SubElement(xmlRootElement, 'command')
        xmlCommandElement.text = 'PotreeConverter --outdir ' + localOutputFolder + ' --levels ' + str(levels) + ' --output-format ' + str(outputFormat).upper() + ' --source ' + tile + ' --spacing ' + str(spacing) + ' --aabb "' + extent + '"'

        xmlOutputElement = etree.SubElement(xmlRootElement, 'output')
        xmlOutputElement.text = localOutputFolder

    oFile.write(etree.tostring(rootOutput, pretty_print=True, encoding='utf-8').decode('utf-8'))
    oFile.close()


def argument_parser():
   # define argument menu
    parser = argparse.ArgumentParser(
    description="Creates a parallel commands XML configuration file. This XML file can be used with pycoeman to run the tasks in a SGE cluster, in a bunch of ssh-reachable hosts or in the local machine"
    parser.add_argument('-i','--input',default='',help='Input folder with the tiles. This folder must contain subfolders, one for each tile. Each tile subfolder must contain the LAS/LAZ files in the tile',type=str, required=True)
    parser.add_argument('-o','--output',default='',help='Output parallel commands XML configuration file',type=str, required=True)
    parser.add_argument('-f','--format',default='',help='Format (LAS or LAZ)',type=str, required=True)
    parser.add_argument('-l','--levels',default='',help='Number of levels for OctTree',type=int, required=True)
    parser.add_argument('-s','--spacing',default='',help='Spacing at root level',type=int, required=True)
    parser.add_argument('-e','--extent',default='',help='Extent to be used for all the OctTree, specify as "minX minY minZ maxX maxY maxZ"',type=str, required=True)
    return parser

def main():
    args = argument_parser().parse_args()
    print 'Input folder: ', args.input
    print 'Output file: ', args.output
    print 'Format: ', args.format
    print 'Levels: ', args.levels
    print 'Spacing: ', args.spacing
    print 'Extent: ', args.extent

    run(args.input, args.output, args.format, args.levels, args.spacing, args.extent)

if __name__ == "__main__":
    main()
