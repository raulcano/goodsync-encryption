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

# import csv
# from datetime import datetime
# import re
# import codecs

####################################################
# Constants definition
####################################################

AXCRYPT_EXE = os.environ['ProgramFiles']+'\Axantum\AxCrypt\AxCrypt.exe'

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
	print "   [phase]: is the GoodSync phase. Either PA -PreAnalysis, for encryption- or PS -PostSync, for"
	print "                decryption-"
	print "   [pass]: is the encryption passphrase"
	print "   [dir]: is the root folder where the encryption has to start. Do not add trailing slash!"
	print "   [recursive]: can be -m or empty. If -m , then the encryption applies to all the subdirectories"
	print " Examples:"
	print "   GoodSync-Encrypt-Decrypt.bat PA test \"test axcrypt dir\" -m"
	print "   GoodSync-Encrypt-Decrypt.bat PS test \"test axcrypt dir\" -m "
	print "   GoodSync-Encrypt-Decrypt.bat PA test \"test axcrypt dir\""
	print "   GoodSync-Encrypt-Decrypt.bat PA \"test password with blank spaces\" \"my/directory/here\""
	print "   GoodSync-Encrypt-Decrypt.bat PA \"passwordNoSpacesAndInsideQuotes\" \"my/directory/here\""
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
if phase != "PA" and phase != "PS":
	print 'Wrong fist parameter. Use one of the following:'
	print 'PA: Pre Analysis, for encryption'
	print 'PS: Post Sync, for decryption'
	sys.exit()

if recursion != "-m" and recursion != "":
	print 'Wrong recursion parameter. Use one of the following:'
	print '-m: Recursive encription/decryption within the directory'
	print '[empty]: Encryption/decryption only in the current directory'
	sys.exit()

try:
	# Get the files' attributes (time, etc.)
	# One array with the attributes we'll store
	# One associative array with the name of the file as index linking to the array of attributes
	# This array must be saved applied to the encrypted version of the files
	
	# NOTE: don't forget to include the recursion
	
	# for filename in os.listdir('.'):
		# info = os.stat(filename)
		# print info.st_mtime
		# ...
	if phase == "PA":
		# To be executed in the "Pre-Analyze" step

		# Encrypt the files with the given passphrase, but do not remember this passphrase
		# This removes the original file and leaves the encrypted version only. After the syncronization
		# the files are decrypted back to the local system. 
		# See the "PS" part of this script
		
		args = [AXCRYPT_EXE, '-b','2','-e','-k',passphrase,recursion,'-z',path+'\*']
		subprocess.call(args)
		
		# Rename all just encrypted files to anonymous names
		# args = [AXCRYPT_EXE, recursion,'-h',path+'\*.axx']
		# subprocess.call(args)
		
	elif phase == "PS":
		print ''
		# To be executed in the "Post-Sync" and "Post-Analysis with no changes" step
		# Decrypt all the encrypted files in the directory and clear the cache
		args = [AXCRYPT_EXE, '-b','2','-k',passphrase,recursion,'-f','-d',path+'\*.axx','-t']
		subprocess.call(args)
		
		# Request that the resident process ends itself, and exits
		args = [AXCRYPT_EXE, '-x']
		subprocess.call(args)
	
	# Here we apply to the newly created files the attributes we stored previously
	# ...
except:
	print '==========================='
	print 'Errors found:'
	print ''
	print "Unexpected error:", sys.exc_info()[0]
	print ''
	print '==========================='
	raise
