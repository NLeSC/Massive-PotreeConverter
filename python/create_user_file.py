#!/usr/bin/env python
"""Creates a PC file with a selection of points from a BBox and level"""

import argparse, traceback, time, os, psycopg2
import utils

USERNAME = utils.getUserName()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""Creates a PC file with a selection of points from a BBox and level""")
    parser.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    parser.add_argument('-e','--mail',   default='',help='E-mail address to send e-mail after completion',type=str, required=True)
    parser.add_argument('-l','--level',  default='',help='Level of data used for the generation (only used if the used table is the one with the potree data). If not provided the raw data is used',type=str)
    parser.add_argument('-b','--bbox',   default='', help='Bounding box for the points selection given as minX,minY,maxX,maxY',required=True)
    parser.add_argument('-d','--dbname',default=utils.DB_NAME,help='Postgres DB name [default ' + utils.DB_NAME + ']',type=str)
    parser.add_argument('-u','--dbuser', default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass', default='',help='DB pass',type=str)
    parser.add_argument('-t','--dbhost', default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport', default='',help='DB port',type=str)
    parser.add_argument('-w','--baseurl', default='',help='Base URL for the output file (web access)',type=str)
    parser.add_argument('-f','--basepath', default='',help='Base path for the output file (internal access)',type=str)
    return parser


def run(srid, userMail, level, bBox, dbName, dbPass, dbUser, dbHost, dbPort, baseURL, basePath):
    message = ''
    statusOk = True
    
    try:
        # Get the extent of the bounding boxes anc check they are float values
        (minX,minY,maxX,maxY) = bBox.split(',')
        for v in (minX,minY,maxX,maxY):
            float(v)
        
        # Make connection
        connectionString = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
        connection = psycopg2.connect(connectionString)
        cursor = connection.cursor()
        
        cursor.execute('SELECT max(level) FROM ' + utils.DB_TABLE_POTREE)
        maxLevelPotree = cursor.fetchone()[0]

#        print level,maxLevelPotree
        if level != '':
            if int(level) <= maxLevelPotree:
                dbTable = utils.DB_TABLE_POTREE
            else:
                raise Exception('Specified level (' + level + ') is not available in the potree data')
        else:
            dbTable = utils.DB_TABLE_RAW
            
        
        outputFileName = '%s_%s_%s_%s_%d.laz' % (minX,minY,maxX,maxY,srid)
        outputAbsPath = basePath + '/' + outputFileName
        
        if os.path.isfile(outputAbsPath):
            raise Exception('The file already existed!')
        else:
            query = 'SELECT filepath FROM ' + dbTable + ' where ST_Intersects(ST_MakeEnvelope(' + minX + ', ' + minY + ', ' + maxX + ', ' + maxY + ', ' + str(srid) + '), geom)'
            if dbTable == utils.DB_TABLE_POTREE:
                query += ' AND level = ' + str(level)
            
            inputList = outputAbsPath + '.list'
            connectionStringCommandLine = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort, cline = True)
            precommand = 'psql ' + connectionStringCommandLine + ' -t -A -c "' + query + '" > ' + inputList
            print precommand
            os.system(precommand)
            
            command = 'lasmerge -lof ' + inputList + ' -inside ' + minX + ' ' + minY + ' ' + maxX + ' ' + maxY + ' -merged -o ' + outputAbsPath
            print command
            os.system(command)
    except:
        statusOk = False
        message = 'There was some error in the file generation: ' + traceback.format_exc()
    
    
    if os.path.isfile(outputAbsPath) and statusOk:
        (count, _, _, _, _, _, _, _, _, _, _, _, _) = utils.getPCFileDetails(outputAbsPath)
        size = utils.getFileSize(outputAbsPath)
        
        content = """Subject: Data is ready

Your selected data is ready. %d points were selected and stored in %s with a size of %d MB.

Please download your data asap. This data will be deleted after 24 hours.

""" % (count, outputAbsPath.replace(basePath, baseURL), size)
    
    else:
        content = """Subject: Data is NOT ready

Your selection could not be stored. Sorry for the inconveniences."""

    content += message

    mailFileAbsPath = outputAbsPath + '.mail'
    mailFile = open(mailFileAbsPath, 'w')
    mailFile.write(content)
    mailFile.close()
    
    os.system('sendmail ' + userMail + ' < ' + mailFileAbsPath)
    

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'SRID: ', args.srid
    print 'E-mail: ', args.mail
    print 'Level: ', args.level
    print 'BBox: ', args.bbox
    print 'DB name: ', args.dbname
    print 'DB user: ', args.dbuser
    print 'DB pass: ', '*'*len(args.dbpass)
    print 'DB host: ', args.dbhost
    print 'DB port: ', args.dbport
    print 'Base Web URL: ', args.baseurl
    print 'Base path: ', args.basepath
    
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.srid, args.mail, args.level, args.bbox, args.dbname, args.dbpass, args.dbuser, args.dbhost, args.dbport, args.baseurl, args.basepath)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
