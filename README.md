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

Python Lib Script to load 

### Sources

List of sources to be backup. Source attributes are type dependent.
#### Directory
  Backup a directory.
  - name
    NAme of the source, use to create archive file
  - path
    Path of the Directory to be backuped
  - gzip
    use gZip compression, archive name is name.tgz then
  - bzip
    use bZip compression, archive name is name.tbz then
  
#### MySQL
  Backup sql Database
  - name
    NAme of the source, use to create archive file.
  - host / socket 
    Specify the hostname (host) or the socket (socket) to use, do not specify for localhost
  - user
    username used to  connect to database
  - passwd
    password...
  - database
  


### Destinations

List of destinations

### Backup Routes

link between source and destination
