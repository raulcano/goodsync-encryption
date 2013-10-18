# -*- coding: utf-8 -*-
# ================================================================================
# == Encryption/Decryption script for GoodSync
# == Author: Raul Cano Argamasilla (raul.cano.argamasilla@gmail.com)
# == Date: 2013-10-14
# ================================================================================

# ================================================================================
# == Requirements
# ================================================================================
# Requirements:
#   GoodSync (Windows version)
#   AxCrypt (Windows version)

#=================================================================================
# == Description
# ================================================================================
# This is a script to be used by GoodSync in order to keep a remote encrypted repository of 
# ALL the files in a local directory. The synchronization is kept between
# the local files (not encrypted) and the remote copies (encrypted).
# The concept is easy but can be tricky:
# - The user synchronizes his local files with a remote repository (e.g. a cloud server, network drive)
# - The files in the remote repo will be only encrypted files, so we can use a third party provider
#   and forget about any concerns on privacy.
# - If another user wants to use the same files from that repo, the system will keep in sync even
#   with the encrypted files in the remote repo.
# - The remote repo can serve, therefore, as a backup or middle repository, ALWAYS KEEPING PRIVACY.
# - If different users want to use the same repository, they will have to use the same encrypting key.
#
# Typical use case:
# 1.The user creates a job to be synced with a cloud repository (or another folder, whatever).
# 2.Everytime the job is run, all the files on that folder are automatically encrypted and the 
#   originals are deleted temporarily, leaving the encrypted versions only in the local directory.
# 3.The analysis and comparison of versions is done among only the encrypted files in both sides(L #   and R).
# 4a.If changes are detected, the corresponding files will be synced (either uploaded or downloaded)  
# 4b.If no changes are detected, nothing happens.
# 5.Finally, the local files are decrypted back in the local directory, leaving only plain
#   unencrypted files there (no encrypted files will remain at this point).
#
# Note: We decided to encrypt every single file every time the job is called.
# If we only encrypted the recently changed files the files that are not encrypted in 
# this step remain unencrypted in the directory and are synced via GoodSync as plain format,
# something we don't want. For sure there are more elegant ways to approach that but they are
# out of scope.
#	 
# ================================================================================
# == Usage of the script
# ================================================================================

# ====================
# Usage in GoodSync 
# ====================
# Usage in GoodSync:
# Note: The usage must be coherent in all the command lines. That is to say, the passphrase,
# directory and recursion parameter (-m) must equal for Pre-Analysis, Post-Analysis and Post-Sync.
# Therefore, within the Automation section of a job, add the following commands.
#
# Pre Analysis:
# [Route_to_script\]GoodSync-Encrypt-Decrypt.py PA "[my_passphrase]" "[my_directory]" [-m]
# Post Analysis with no changes:
# [Route_to_script\]GoodSync-Encrypt-Decrypt.py PS "[my_passphrase]" "[my_directory]" [-m]
# Post Sync:
# [Route_to_script\]GoodSync-Encrypt-Decrypt.py PS "[my_passphrase]" "[my_directory]" [-m]
# 
# =====================
# Usage in command line 
# =====================
# Usage in command line:
# GoodSync-Encrypt-Decrypt.py <phase> <pass> <dir> <recursive>
#   <phase> (%1) is the GoodSync phase. Either PA (PreAnalysis, for encryption) or PS (PostSync, for
#                decryption)
#   <pass> (%2) is the encryption passphrase
#   <dir> (%3) is the root folder where the encryption has to start. Do not add trailing slash!
#   <recursive> (%4) can be -m or empty. If -m , then the encryption applies to all the subdirectories
	# Put it on the same directory as the script and the input file. 
	

# ====================
# Examples
# ====================
#   GoodSync-Encrypt-Decrypt.py PA test "test axcrypt" -m
#   GoodSync-Encrypt-Decrypt.py PS test "test axcrypt" -m 
#   GoodSync-Encrypt-Decrypt.py PA test "test axcrypt"
#   GoodSync-Encrypt-Decrypt.py PA "test password with blank spaces" "test axcrypt"
#   GoodSync-Encrypt-Decrypt.py PA "passwordNoSpacesAndInsideQuotes" "test axcrypt"
#   GoodSync-Encrypt-Decrypt.py PA "test" "C:\Users\raul cano\Documents\temp\test axcrypt" -m
# ================================================================================


####################################################
# Imports
####################################################
import sys
import os
import subprocess
import re
from datetime import datetime, tzinfo, timedelta
import fnmatch

####################################################
# Constants definition
####################################################

AXCRYPT_EXE = os.environ['ProgramFiles']+'\Axantum\AxCrypt\AxCrypt.exe'
AXCRYPT_EXTENSION = '.axx'
PHASE_PA = 'PA'
PHASE_PS = 'PS'
RECURSION_YES = '-m'
RECURSION_NO = ''
SEP_1 = '\\'
SEP_2 = '/'
# The ones needed by GoodSync to work, we don't encrypt them in any case
# In principle it's only _gsdata_ since _saved_ and _history_ are included there
DIRECTORIES_TO_SKIP = "_gsdata_"


####################################################
# Arguments processing
####################################################

if (len(sys.argv)==4):
	phase = sys.argv[1]
	passphrase = sys.argv[2]
	path = sys.argv[3]
	recursion = ''
elif (len(sys.argv)==5):
	phase = sys.argv[1]
	passphrase = sys.argv[2]
	path = sys.argv[3]
	recursion = sys.argv[4]
else:
	print "Wrong number of arguments: ", len(sys.argv)
	print "Usage:"
	print " {0} [phase] [pass] [dir] [recursive]".format(sys.argv[0])
	print "   [phase]: is the GoodSync phase. Either " + PHASE_PA + " -PreAnalysis, for encryption- or " + PHASE_PA + " -PostSync, for"
	print "                decryption-"
	print "   [pass]: is the encryption passphrase"
	print "   [dir]: is the root folder where the encryption has to start. Do not add trailing slash!"
	print "   [recursive]: can be -m or empty. If -m , then the encryption applies to all the subdirectories"
	print " Examples:"
	print "   GoodSync-Encrypt-Decrypt.bat " + PHASE_PA + " test \"test axcrypt dir\" -m"
	print "   GoodSync-Encrypt-Decrypt.bat " + PHASE_PA + " test \"test axcrypt dir\" -m "
	print "   GoodSync-Encrypt-Decrypt.bat " + PHASE_PA + " test \"test axcrypt dir\""
	print "   GoodSync-Encrypt-Decrypt.bat " + PHASE_PA + " \"test password with blank spaces\" \"my/directory/here\""
	print "   GoodSync-Encrypt-Decrypt.bat " + PHASE_PA + " \"passwordNoSpacesAndInsideQuotes\" \"my/directory/here\""
	sys.exit()

print '==========================='
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Script name: ', sys.argv[0]
print 'Phase: ', phase
print 'Passphrase: ', passphrase
print 'Path: ', path
print 'Recursion: ', recursion
print ''


# Check the arguments "phase" and "recursive"
if phase != PHASE_PA and phase != PHASE_PS:
	print 'Wrong fist parameter. Use one of the following:'
	print PHASE_PA + ': Pre Analysis, for encryption'
	print PHASE_PS + ': Post Sync, for decryption'
	sys.exit()

if recursion != RECURSION_YES and recursion != "":
	print 'Wrong recursion parameter. Use one of the following:'
	print '-m: Recursive encription/decryption within the directory'
	print '[empty]: Encryption/decryption only in the current directory'
	sys.exit()

# Check the arguments for including / excluding files and folders
includes = ['*'] # for files only
excludes = ['test\_gsdata_'] # for dirs and files
####################################################
# Functions
####################################################

class UTC(tzinfo):
    def utcoffset(self, dt):
         return timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return timedelta(0)
		
def printNice(files_times):
	for name, times in files_times.items():
		t1 = datetime.fromtimestamp(float(times[0]), UTC())
		t2 = datetime.fromtimestamp(float(times[1]), UTC())
		print 'File                  : ' + name
		print 'Last access time      : ' + str(t1)
		print 'Last modification time: ' + str(t2)
		print '=='


def getFilesTimes(path,recursion, includes, excludes):
	# One array with the attributes we'll store
	# One associative array with the name of the file as index linking to the array of attributes
	# This array must be saved applied to the encrypted version of the files
	# http://docs.python.org/2/library/os.html#os.stat
	files_times = {} 

	# for root, dirs, files in os.walk(path):
		# for name in files:
			# info = os.stat(os.path.join(root,name))
			# # [time of most recent content modification, time of most recent access]
			# files_times[os.path.join(root,name)] = [info.st_atime, info.st_mtime]
		# if recursion != RECURSION_YES: dirs[:] = []	
	
	# transform glob patterns to regular expressions
	includes = r'|'.join([fnmatch.translate(x) for x in includes])
	excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
	for root, dirs, files in os.walk(path):
		# print 'Root:                   '+root
		# print 'Dirs before exclusion:  '+str(dirs)
		# exclude dirs
		dirs[:] = [os.path.join(root, d) for d in dirs]
		dirs[:] = [d.replace(root+SEP_1,'',1) for d in dirs if not re.match(excludes, d)]

		# print 'Dirs after exclusion:   '+str(dirs)

		# exclude/include files
		# print 'Files before exclusion: '+str(files)
		files = [os.path.join(root, f) for f in files]
		files = [f for f in files if not re.match(excludes, f)]
		files = [f for f in files if re.match(includes, f)]
		# print 'Files before exclusion: '+str(files)
		
		for fname in files:
			info = os.stat(fname)
			# [time of most recent content modification, time of most recent access]
			files_times[fname] = [info.st_atime, info.st_mtime]
		
		if recursion != RECURSION_YES: 
			dirs[:] = []	
		
	return files_times
	
	

def setFilesTimes(path, recursion, new_files_times):
	# looks in the path and matches the files from the array 
	# http://www.gubatron.com/blog/2007/05/29/how-to-update-file-timestamps-in-python/	

	for file, times in new_files_times.items():
		t = times[0], times[1]
		os.utime(os.path.join(file),t)
	
# If PHASE_PA change names from their originals to the encrypted format (e.g. file.txt --> file-txt.axx)
# If PHASE_PS change names from their encrypted format to their original(e.g. file-txt.axx --> file.txt)
def rename(files_times, phase):
	
	new_files_times = {}
	# print files_times
	for name,times in files_times.items():
		parts = name[::-1].partition(SEP_1)
		# if no partition produced, may be because the separator is other type (/ instead of \)
		if parts[1] == '' and parts[2] == '':
			parts = name[::-1].partition(SEP_2)
		name2 = parts[0]
		# here, name has the reversed name of the file
		
		if phase == PHASE_PA:
			# since the string is reversed
			# 1.- substitute the first dot for a dash
			name2 = name2.replace('.','-',1)
			# 2.- prepend the reversed AXCRYPT_EXTENSION
			name2 = AXCRYPT_EXTENSION[::-1] + name2
			
		elif phase == PHASE_PS:
			# since the string is reversed
			# 1.- remove the first occurence of (reversed AXCRYPT_EXTENSION)
			name2 = name2.replace(AXCRYPT_EXTENSION[::-1],'',1)
			# 2.- replace the first occurence of '-' for '.'
			# This has a problem though, if the original file had no extension and a dash on its name
			# the new name will include a dot instead of a dash as originally expected
			name2 = name2.replace('-','.',1)
			
		# Reconstruct the path with the new filename and the path (as from "parts")
		new_path = parts[2][::-1] + parts[1] + name2[::-1]
		new_files_times[new_path] = times

	return new_files_times
			
try:
	# Get the files' attributes (time, etc.)
	files_times = getFilesTimes(path, recursion, includes, excludes)
	if phase == PHASE_PA:
	
		# To be executed in the "Pre-Analyze" step

		# Encrypt the files with the given passphrase, but do not remember this passphrase
		# This removes the original file and leaves the encrypted version only. After the syncronization
		# the files are decrypted back to the local system. 
		# See the PHASE_PS part of this script
		
		# args = [AXCRYPT_EXE, '-b','2','-e','-k',passphrase,recursion,'-z',path+'\*']
		# subprocess.call(args)
		
		for file, times in files_times.items():
			args = [AXCRYPT_EXE, '-b','2','-e','-k',passphrase,recursion,'-z',file]
			subprocess.call(args)
		
		# Rename all just encrypted files to anonymous names
		# args = [AXCRYPT_EXE, recursion,'-h',path+'\*.axx']
		# subprocess.call(args)
		
	elif phase == PHASE_PS:
		# To be executed in the "Post-Sync" and "Post-Analysis with no changes" step
		# Decrypt all the encrypted files in the directory and clear the cache
		# args = [AXCRYPT_EXE, '-b','2','-k',passphrase,recursion,'-f','-d',path+'\*.axx','-t']
		# subprocess.call(args)
		
		for file, times in files_times.items():
			args = [AXCRYPT_EXE, '-b','2','-k',passphrase,recursion,'-f','-d',file,'-t']
			subprocess.call(args)
		
		# Request that the resident process ends itself, and exits
		args = [AXCRYPT_EXE, '-x']
		subprocess.call(args)
	
	# replace the names of the files from the unencrypted version to the encrypted
	new_files_times = rename(files_times, phase)
	# Here we apply to the newly created files the attributes we stored previously
	setFilesTimes(path, recursion, new_files_times)

except:
	print '==========================='
	print 'Errors found:'
	print ''
	print "Unexpected error:", sys.exc_info()[0]
	print ''
	print '==========================='
	raise
