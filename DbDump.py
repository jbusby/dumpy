#!/usr/bin/env python
#-----------------------------------------------------------------------------
# This script opens a connection to a database and loops through each table
# generating a mysqldump and then bzipping and pushing the file to a remote
# backup server.  An optional email is sent when the job is finished.
#-----------------------------------------------------------------------------
# Author    Jeff Busby <jeff@jeffbusby.ca>
#-----------------------------------------------------------------------------
import subprocess as sub
import os
import sys
import time
import smtplib
from ProgressBar import ProgressBar
from email.mime.text import MIMEText

class DbDump:
    """
    validates parameters and executles the transfer of db dumps to a remote backup server
    """
    def __init__(self, config, opts):
        self.__conf={} 
        self.__opts={}
        self.__feedback=[]
        self.__errors=[]
        self.__conf["db_host"]        = config.get('dbbackup', 'database_host')
        self.__conf["db_name"]        = config.get('dbbackup', 'database_name')
        self.__conf["db_user"]        = config.get('dbbackup', 'database_user')
        self.__conf["db_password"]    = config.get('dbbackup', 'database_password')
        self.__conf["remote_dir"]     = config.get('common', 'remote_dir')
        self.__conf["remote_port"]    = config.get('common', 'remote_port')
        self.__conf["remote_user"]    = config.get('common', 'remote_user')
        self.__conf["remote_host"]    = config.get('common', 'remote_host')
        self.__conf["email_on"]       = config.get('common', 'email_on')
        self.__conf["email_sender"]   = config.get('common', 'email_sender')
        self.__conf["email_receiver"] = config.get('common', 'email_receiver')
        self.__conf["email_smtp"]     = config.get('common', 'email_smtp')
        self.__conf["email_port"]     = config.get('common', 'email_port')
        self.__opts["verbose"]        = opts.verbose
        self.__opts["dryrun"]         = opts.dryrun

    def __validate(self):
        """ 
        Validates the config params and options 
        """
        if self.__conf["db_name"]==None or self.__conf["db_user"]==None or self.__conf["db_password"]==None or self.__conf["remote_dir"]==None :
            p.error("Missing mandatory config options")
            p.print_help()
            sys.exit(2)
    
    def run(self):
        """
        Executes neccessary shell commands to dump the database tables to the remote host
        """
        self.__validate()
        if self.__opts["verbose"]:
            print "Config is valid."
            
        tables = self.__getTables()
        if self.__opts["verbose"]:
            totalTables = len(tables)
            print str(totalTables) + " table(s) fetched, beginning dump.\n\n"
            prog = ProgressBar(0, totalTables, 77, mode='fixed', char='#')
            
        for i, table in enumerate(tables):
            table = table.rstrip()
                
            if self.__dumpTable(table)==False:
                self.__sendEmailNotification()
                print self.__errors
                sys.exit(2)
            
            if self.__opts["verbose"]:
                prog.increment_amount()
                print prog, '\n',
                sys.stdout.flush()
                
        if self.__opts["verbose"]:
            print self.__getFeedback()

        self.__sendEmailNotification()

    def __dumpTable(self, tableName):
        """
        Builds the mysqldump command line string and executes.  stderr is piped to sub and if any errors
        are found they are appended to the error list and the method returns false
        Returns bool(True|False) True on success
        """
        dumpCommand = ('mysqldump --opt -Q -u' + self.__conf["db_user"] + self.__getPasswordString() + ' ' 
                    + self.__conf["db_name"] + ' ' + tableName + ' | bzip2 -c | ssh -p ' + self.__conf["remote_port"] + ' ' 
                    + self.__conf["remote_user"] + '@' + self.__conf["remote_host"] + ' "cat > ' 
                    + self.__conf["remote_dir"] + '/' + tableName + '.sql.bz2"')
        dc = sub.Popen(dumpCommand, shell=True, stderr=sub.PIPE)
        errs = dc.stderr.readlines()
        if errs:
            self.__errors.append(errs)
            return False
        
        return True
        
    def __getPasswordString(self):
        """
        If the password is present in the config file then it formats for use with both the 
        mysql and mysqldump commands.  This is to get around the password prompt when no password
        is supplied
        Returns string pw
        """
        pw=""
        if self.__conf["db_password"] != "":
            pw=" -p" + self.__conf["db_password"] 
        return pw
    
    def __getTables(self):
        """ 
        Returns a list of tables for the database that is being backedup 
        """
        command=("mysql -u" + self.__conf["db_user"] + self.__getPasswordString() 
               + " " + self.__conf["db_name"] + " -e 'show tables' | egrep -v 'Tables_in_'")
        
        p = sub.Popen(command, shell=True, stdout=sub.PIPE)
        return p.stdout.readlines()
        
    def __sendEmailNotification(self):
        """
        Sends email notifiction
        """
        if self.__conf["email_on"]:
            msg = MIMEText(self.__getFeedback())
            msg['Subject'] = 'Database Dump Complete for ' + os.uname()[1]
            msg['From'] = self.__conf["email_sender"]
            msg['To'] = self.__conf["email_receiver"]
    
            s = smtplib.SMTP(self.__conf["email_smtp"], self.__conf["email_port"])
            s.sendmail(msg['From'], msg['To'], msg.as_string())
            s.quit()

    def __getFeedback(self):
        """
        Formats a feedback message with regards to the backup, used for email notification and 
        verbose enabled script execution.
        Returns a string
        """  
        
        ret="""
           -------------------------------------------'         
           Database backup completed for ' + os.uname()[1] + ' on ' + time.ctime()
           -------------------------------------------') 
           Database Host: """ + self.__conf["db_host"] + """ 
           Database Name:  """ + self.__conf["db_name"] + """  
           Backup Host:  """ + self.__conf["remote_host"] + """ 
           Backup Directory:  """ + self.__conf["remote_dir"] + """ 
           --------------------------------------------
        """
        
        if self.__errors:
            ret+='Errors occurred during backup:\n\n'
            for error in self.__errors:
                ret+=str(error)
            ret+='\n--------------------------------------------\n\n'
        
        for message in self.__feedback:
            ret+=message
        
        return ret