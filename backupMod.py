import sys
import tarfile
import os
import time
import shutil
from datetime import date
from ftplib import FTP
import gzip
from subprocess import Popen, PIPE
from threading import Thread

__name__ = "backupMod"

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
	today = date.today()
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

def cdTree(dir,ftp):
	if dir != "":
		try:
			ftp.cwd(dir)
		except:
			cdTree("/".join(dir.split("/")[:-1]), ftp)
			ftp.mkd(dir)
			ftp.cwd(dir)

def Destination_Ftp(file, destination,configuration):
	global date, config, FTP
	today = date.today()
	format = "/%Y/%m/%d"
	if destination.get('format'):
		format = destination.get('format')
		
	dest=  today.strftime(format)  
	#connect to ftp
	ftp = FTP(destination.get('host'))     # connect to host, default port
	ftp.login( destination.get('user') , destination.get('passwd') )
	cdTree(dest,ftp) # creation de l'arborescence
	handle = open(file, 'rb') # on ouvre le fichier en mode read-binary
	ftp.storbinary('STOR '+ os.path.basename(file), handle) # envoi
	handle.close() # fermeture du fichier
	ftp.close()
