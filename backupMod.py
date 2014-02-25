import sys
import tarfile
import os
import time
import shutil
import datetime 
from ftplib import FTP
import gzip
from subprocess import Popen, PIPE
from threading import Thread
import re

__name__ = "backupMod"
Rdir = re.compile('^d.{9,9}\s+\d+\s+\d+\s+\w+\s+\d+\s+(.*)\s+(.*)$')
Rfil = re.compile('^-.{9,9}\s+\d+\s+\d+\s+\w+\s+\d+\s+(.*)\s+(.*)$')


def Source_Directory(source,configuration):
	
	global tarfile,os
	
	path = source.get('path') + '/'
	if source.get('gzip'):
		suffix = ".tgz"
		mode = "w|gz"
	elif source.get('bzip'):
		suffix = ".tbz"
		mode = "w|bz2"
	else: #no compression
		suffix = ".tar"
		mode = "w"
		
	mytarfile = configuration.find('workingdir').text + "/" + source.get('name') + suffix
	tar = tarfile.open(mytarfile, "w")
	for filename in os.listdir(path):
		print( path +  filename)
		tar.add(path + filename)	
	
	tar.close()
	return mytarfile

def f(input, output):
    for line in iter(input.readline, ''):
        output.write(line)

def Source_Mysql(source,configuration):
	global tarfile,os
	myfile = configuration.find('workingdir').text + "/" + source.get('name') +'.gz'
	if source.get('socket'):
		args = ['mysqldump', '-S', source.get('socket'), '-u', source.get('user'), '-p' + source.get('passwd'), '--add-drop-database', '--databases', source.get('database')]
	elif source.get('host'):
		args = ['mysqldump', '-h', source.get('host'), '-u', source.get('user'), '-p' + source.get('passwd'), '--add-drop-database', '--databases', source.get('database')]
	else:
		args = ['mysqldump', '-u', source.get('user'), '-p' + source.get('passwd'), '--add-drop-database', '--databases', source.get('database')]
	p = Popen(args, bufsize=-1, stdin=PIPE, stdout=PIPE)
	t=Thread(target=f, args=(p.stdout, gzip.open( myfile, 'wb')))
	t.start()
	t.join()
	return myfile


def Destination_Directory(file, destination,configuration):
	global date, config,os,shutil
	today = datetime.date.today()
	format = "/%Y/%m/%d"
	if destination.get('format'):
		format = destination.get('format')

	#create directory if necessary
	dest= destination.get('path') + today.strftime(format)  
	d = os.path.normpath(dest)
	if not os.path.exists(d):
		os.makedirs(d)
	
	fulldest = os.path.normpath( dest + '/' + os.path.basename(file) )
	shutil.move(file,fulldest)
	#Prune
	if destination.get('prune'):
		#list directory
		deldir=[]
		dayold = int(destination.get('prune')) * 86400
		present = time.time()
		for root, dirs,files in os.walk(destination.get('path'), topdown=False):
			for name in dirs:
				if present - os.path.getmtime(os.path.join(root,name)) > dayold:
					countDir = 0
					#change root
					nroot = os.path.join(root,name)
					for f in os.listdir(os.path.join(root,name)):
						if os.path.isdir(os.path.join(nroot,f)):
							countDir+=1
					if countDir == 0:
						deldir.append( os.path.join(root,name) )
		for dir in deldir:
			for f in os.listdir(dir):
				os.remove(os.path.join(dir,f) )
			os.rmdir( dir)


def cdTree(dir,ftp):
	if dir != "":
		try:
			ftp.cwd(dir)
		except:
			cdTree("/".join(dir.split("/")[:-1]), ftp)
			ftp.mkd(dir)
			ftp.cwd(dir)

def rEraseDir(dirName, mtime, present, olddays,ftp):
	data = []
	ftp.dir(data.append)
	empty = True
	for line in data:
		m = Rdir.match(line)
		if m:
			dirEmpty = False
			if m.group(1).find(':')==-1: 
				ftp.cwd( m.group(2) )
				dirEmpty = rEraseDir(m.group(2), time.strptime(m.group(1),'%b %d %Y'),present, olddays,ftp )
				ftp.cwd('..')
			else:
				ftp.cwd( m.group(2) )
				dirEmpty = rEraseDir(m.group(2), time.strptime( time.strftime('%Y ') + m.group(1) , '%Y %b %d %H:%M'),present, olddays,ftp)				
				ftp.cwd('..')
			if dirEmpty:
				ftp.rmd(m.group(2))
				
			empty = dirEmpty
		else:
			result = Rfil.match(line)
			if result:
				if result.group(1).find(':')==-1: 
					if(present -  time.mktime(time.strptime(result.group(1),'%b %d %Y') ) )> olddays:
						ftp.delete( result.group(2))
					else:
						empty = False
				else:
					if(present -  time.mktime(time.strptime( time.strftime('%Y ') + result.group(1) , '%Y %b %d %H:%M')) )> olddays:
						ftp.delete( result.group(2))
					else: 
						empty = False
			else:
				print('Error : ' + line )
	return empty
	
def Destination_Ftp(file, destination,configuration):
	global date, config, FTP
	today = datetime.date.today()
	format = "/%Y/%m/%d"
	if destination.get('format'):
		format = destination.get('format')
		
	dest=destination.get('path') +  today.strftime(format) 
	#connect to ftp
	ftp = FTP(destination.get('host'))     # connect to host, default port
	ftp.login( destination.get('user') , destination.get('passwd') )
	cdTree(dest,ftp) # creation de l'arborescence
	handle = open(file, 'rb') # on ouvre le fichier en mode read-binary
	ftp.storbinary('STOR '+ os.path.basename(file), handle) # envoi
	handle.close() # fermeture du fichier
	if destination.get('prune'):
		ftp.cwd(destination.get('path') )
		olddays = int(destination.get('prune')) * 86400
		present = time.time()
		rEraseDir(destination.get('path'), present,present,olddays,ftp)
	ftp.close()
