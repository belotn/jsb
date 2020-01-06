# jsb

Just a Single Backup Tool

## Purpose

An easy and reliable backup tool
By default, it looks for file backup.xml in the working directory

## XML Syntax
### Configuration

Configuration Items

#### WorkingDir

Where should i work.

#### Lib

Python Lib Script to load, by default backupMod incule Directory, Mysql and FTP backup functions

### Sources

List of sources to be backup. Source attributes are type dependent.
#### Directory
Directory to backed up via "tar" utility
##### Attributes
  Backup a directory.
  - name
    Name of the source, use to create archive file and in backup routes.
  - path
    Path of the Directory to be backuped
  - gzip
    use gZip compression, archive name is name.tgz then
  - bzip
    use bZip compression, archive name is name.tbz then
  - type directory
  ##### Examples
  ` <source name="file_wp" type="directory" path="/usr/local/www/wordpress" gzip="true" />`
  
  
#### MySQL
Mysql Databases to be backed up
##### Attributes
  Backup sql Database
  - name
    NAme of the source, use to create archive file and in backup routes.
  - host / socket 
    Specify the hostname (host) or the socket (socket) to use, do not specify for localhost
  - user
    username used to  connect to database
  - passwd
    password...
  - database
    Data to be backuped
  - type mysql
##### Examples
` <source name="db_wp" type="mysql"  socket="/path/to/mysql.sock" user="MyUser" passwd="MyPassword" database="databasename"/>`


### Destinations

List of destinations.

#### Directory
Archive should be copied to this local directory, and it create path PAth/YYYY/MM/DD and save all file under it
##### Attributes
  - name 
    Name of the destination, use in backup routes
  - path 
    Path where archive sould be put.
  - type directory
##### Example
`<destination name="dest" type="directory" path="/var/backups/mybackups" />`
 
#### FTP
Archive should be copied to this ftp directory, and it create path PAth/YYYY/MM/DD and save all file under it
##### Attributes
  - name 
    Name of the destination, use in backup routes.
  - host 
    Ftp server hostname
  - user  
    ftp username
  - passwd 
    ftp password
  - type ftp
##### Example
` <destination name="ftp_dest" type="ftp" host="myhost" user="myuser" passwd="mypass" />`
### Backup Routes
link between source and destination
##### Attributes
  - source
    Name of the source to be backup
  - destination
    Name of the backup destination
##### Example
` <backup source="db_wp" destination="local" />`
