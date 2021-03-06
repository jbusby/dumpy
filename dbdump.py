#!/usr/bin/env python
#-----------------------------------------------------------------------------
#
# This script opens a connection to a database and loops through each table
# generating a mysqldump and then bzipping and pushing the file to a remote
# backup server.  An optional email is sent when the job is finished.
#
# Needs to be run as root to be affective
#
# Usage:  ./dbdump.py -c /path/to/config.cfg
#
#-----------------------------------------------------------------------------
import sys 
import optparse
import cgitb
import ConfigParser
from DbDump import DbDump
cgitb.enable(1, 0, 5, 'text')

def main():
    """
    Parses the configuration file and setups and runs the BackupDb class
    """
    p = optparse.OptionParser(
        description=' Runs a daily backup routine and pushes the files to the backup server',
        prog='dbdump',
        version='0.1',
        usage='%prog -c /path/to/config.cfg'
    )
    p.add_option('-c', '--config')
    p.add_option('-q', '--quiet', action='store_const', const=0, dest='verbose')
    p.add_option('-v', '--verbose', action='store_const', const=1, dest='verbose')
    p.add_option('--noisy', action='store_const', const=2, dest='verbose')
    p.add_option('--dryrun', '-n' )
    p.add_option('--email', '-e' )
    (opts, args) = p.parse_args()
    if opts.config==None:
        p.error("Missing mandatory config options")
        p.print_help()
    
    config = ConfigParser.SafeConfigParser()
    config.read(opts.config)
    dumppy = DbDump(config, opts)
    dumppy.run()

if __name__=='__main__':
    main()