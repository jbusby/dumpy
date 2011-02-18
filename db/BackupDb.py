#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Joyspoon.com
#
# Permission to use, copy, modify, lease, resell, rent, or distribute this
# software and its documentation for any purpose whatsoever, without fee,
# and without a written agreement, is hereby denied.
#
#-----------------------------------------------------------------------------
#
# This script opens a connection to a database and loops through each table
# generating a mysqldump and then bzipping and pushing the file to a remote
# backup server.  An optional email is sent when the job is finished.
#
#
#-----------------------------------------------------------------------------
#
# Copyright (c) Panvista Media Corp. (www.panvistamedia.com)
# Author    Jeff Busby <jeff@jeffbusby.ca>
#
#-----------------------------------------------------------------------------
import subprocess as sub
import os
import time
import smtplib
from email.mime.text import MIMEText

class BackupDb:
    """
    validates parameters and executles the transfer of db dumps to a remote backup server
    """
    def __init__(self, config, opts):
        self.data = {} 
        self.opts = {}
        self.data["db_host"]        = config.get('dbbackup', 'database_host')
        self.data["db_name"]        = config.get('dbbackup', 'database_name')
        self.data["db_user"]        = config.get('dbbackup', 'database_user')
        self.data["db_password"]    = config.get('dbbackup', 'database_password')
        self.data["remote_dir"]     = config.get('dbbackup', 'remote_dir')
        self.data["remote_port"]    = config.get('dbbackup', 'remote_port')
        self.data["remote_user"]    = config.get('dbbackup', 'remote_user')
        self.data["remote_host"]    = config.get('dbbackup', 'remote_host')
        self.data["email_on"]       = config.get('dbbackup', 'email_on')
        self.data["email_sender"]   = config.get('dbbackup', 'email_sender')
        self.data["email_receiver"] = config.get('dbbackup', 'email_receiver')
        self.data["email_smtp"]     = config.get('dbbackup', 'email_smtp')
        self.data["email_port"]     = config.get('dbbackup', 'email_port')
        self.opts["verbose"]        = opts.verbose
        self.opts["dryrun"]         = opts.dryrun

    def validate(self):
       """ 
        Validates the config params and options 
       """
       if self.data["db_name"]==None or self.data["db_user"]==None or self.data["db_password"]==None or self.data["remote_dir"]==None :
           p.error("Missing mandatory config options")
           p.print_help()
           sys.exit(2)
    
    def run(self):
        """
        Executes neccessary shell commands to dump the database tables to the remote host
        """
        command=("mysql -u" + self.data["db_user"] + " -p" + self.data["db_password"]  
               + " " + self.data["db_name"] + " -e 'show tables' | egrep -v 'Tables_in_'")
        p = sub.Popen(command, shell=True, stdout=sub.PIPE)
        tables = p.stdout.readlines()

        for table in tables:
            table = table.rstrip()

            if self.opts["verbose"]:
                print "Dumping " + table

            command2 = ('mysqldump --opt -Q -u' + self.data["db_user"] + '  -p' + self.data["db_password"] + ' ' + self.data["db_name"] + ' ' 
                     + table + ' | bzip2 -c | ssh -p ' + self.data["remote_port"] + ' ' + self.data["remote_user"] 
                     + '@' + self.data["remote_host"] + ' "cat > ' + self.data["remote_dir"] + '/' + table + '.sql.bz2"')
            os.system(command2)
            
        if self.opts["verbose"]:
            print self.getFeedback()

        if self.data["email_on"]:
            self.sendEmailNotification()

    def sendEmailNotification(self):
        """
        Sends email notifiction upon successful dump
        """
        msg = MIMEText(self.getFeedback())
        msg['Subject'] = 'Database Dump Complete for ' + os.environ['HOSTNAME']
        msg['From'] = self.data["email_sender"]
        msg['To'] = self.data["email_receiver"]

        s = smtplib.SMTP(self.data["email_smtp"], self.data["email_port"])
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

    def getFeedback(self):
        """
        Formats a feedback message with regards to the backup, used for email notification and 
        verbose enabled script execution.
        Returns a string
        """  
        ret=('\n\n-------------------------------------------'         
           +'\nDatabase backup completed for ' + os.environ['HOSTNAME'] + ' on ' + time.ctime()
           +'\n-------------------------------------------') 
        output = ({
            'Database Host': self.data["db_host"], 
            'Database Name': self.data["db_name"], 
            'Backup Host': self.data["remote_host"],
            'Backup Directory': self.data["remote_dir"]
        })
        for name, value in output.items():
            ret+='\n%-10s : %10s' % (name, value)
        ret+='\n--------------------------------------------\n\n'
        return ret





