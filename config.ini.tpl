[dbbackup]
;;;;;;;;;;;;;;;;;;;;;
; Database settings ;
;;;;;;;;;;;;;;;;;;;;;
; These are the connection settings of the database that you want to backup

; Database user name
database_user     = 

; Database host (default localhost)
database_host     = localhost

; Database password
database_password = 

; Database name 
database_name     = 

[common]
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Remote Backup Server Settings ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Host name or ip address of remote backup server
remote_host       = 

; Username of backup account on remote server 
remote_user       = 

; Absolute path of backup directory on remote server 
remote_dir        = 

; Port used for backups on remote server (default 22)
remote_port       = 

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Email Notification Settings ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Send email notification on successful backup 1 = yes, 0 = no
email_on          = 0

; Sender's email address
email_sender      = 

; Recipients email address
email_receiver    = 

; SMTP server
email_smtp        =

; SMTP port (default 25)
email_port        =

