#!/usr/bin/env python
"""Creates a PC file with a selection of points from a BBox and level"""

import argparse, traceback, time, os, psycopg2
import utils

USERNAME = utils.getUserName()

def argument_parser():
    """ Define the arguments and return the parser object"""
    parser = argparse.ArgumentParser(
    description="""Creates a PC file with a selection of points from a BBox and level""")
    parser.add_argument('-o','--output',   default='',help='Output file path',type=str, required=True)
    parser.add_argument('-s','--srid',default='',help='SRID',type=int, required=True)
    parser.add_argument('-e','--mail',   default='',help='E-mail address to send e-mail after completion',type=str, required=True)
    parser.add_argument('-l','--level',  default=-1,help='Level of data used for the generation [only used if the used table is the one with the potree data)',type=int)
    parser.add_argument('-b','--bbox',   default='', help='Bounding box for the points selection given as minX,minY,maxX,maxY',required=True)
    parser.add_argument('-d','--dbname',default=utils.DB_NAME,help='Postgres DB name [default ' + utils.DB_NAME + ']',type=str)
    parser.add_argument('-t','--dbtable',default='',help='Table name',type=str, required=True)
    parser.add_argument('-u','--dbuser', default=USERNAME,help='DB user [default ' + USERNAME + ']',type=str)
    parser.add_argument('-p','--dbpass', default='',help='DB pass',type=str)
    parser.add_argument('-b','--dbhost', default='',help='DB host',type=str)
    parser.add_argument('-r','--dbport', default='',help='DB port',type=str)
    return parser


def run(outputAbsPath, srid, userMail, level, bBox, dbName, dbTable, dbPass, dbUser, dbHost, dbPort):
    if os.path.isfile(outputAbsPath):
        raise Exception('Error: ' + outputAbsPath + ' already exists!')
    
    # Make connection
    connectionString = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort)
    connection = psycopg2.connect(connectionString)
    cursor = connection.cursor()
    
    (minX,minY,maxX,maxY) = bBox.split(',')
    
    query = 'SELECT filepath FROM ' + dbTable + ' where ST_Intersects(ST_MakeEnvelope(%s, %s, %s, %s, %s), geom)'
    queryArgs = [minX, minY, maxX, maxY, str(srid)]
    
    if level >= 0:
        query += ' AND level = %s'
        queryArgs.append(str(level))
    
    inputList = outputAbsPath + '.list'
    connectionStringCommandLine = utils.getConnectString(dbName, dbUser, dbPass, dbHost, dbPort, cline = True)
    precommand = 'psql ' + connectionStringCommandLine + ' -t -A -c "' + (query % queryArgs) + '" > ' + inputList
    print precommand
    os.system(precommand)
    
    command = 'lasmerge -lof ' + inputList + ' -inside ' + minX + ' ' + minY + ' ' + maxX + ' ' + maxY + ' -merged -o ' + outputAbsPath
    print command
    os.system(command)
    
    if os.path.isfile(outputAbsPath):
        (_, count, _, _, _, _, _, _, _, _, _, _, _, _) = utils.getPCFileDetails(outputAbsPath, srid)
        size = utils.getFileSize(outputAbsPath)
        
        content = """Subject: Data is ready

Your selected data is ready. %d points were selected and stored in %s with a size of %d MB.

Please download your data asap. This data will be deleted after 24 hours.""" % (count, outputAbsPath, size)
    
    else:
        content = """Subject: Data is NOT ready

Your selection could not be stored. Sorry for the inconveniences."""

    mailFileAbsPath = outputAbsPath + '.mail'
    mailFile = open(mailFileAbsPath, 'w')
    mailFile.write(content)
    mailFile.close()
    
    os.system('sendmail ' + userMail + ' < ' + mailFileAbsPath)
    

if __name__ == "__main__":
    args = argument_parser().parse_args()
    print 'Output file:', args.output
    print 'SRID: ', args.srid
    print 'E-mail: ', args.mail
    print 'Level: ', args.level
    print 'BBox: ', args.bbox
    print 'DB name: ', args.dbname
    print 'DB table: ', args.dbtable
    print 'DB user: ', args.dbuser
    print 'DB pass: ', '*'*len(args.dbpass)
    print 'DB host: ', args.dbhost
    print 'DB port: ', args.dbport
    try:
        t0 = time.time()
        print 'Starting ' + os.path.basename(__file__) + '...'
        run(args.output, args.srid, args.mail, args.level, args.bbox, args.dbname, args.dbtable, args.dbpass, args.dbuser, args.dbhost, args.dbport)
        print 'Finished in %.2f seconds' % (time.time() - t0)
    except:
        print 'Execution failed!'
        print traceback.format_exc()
