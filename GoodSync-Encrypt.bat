ECHO off
REM ***************************************************************************
REM
REM Script Name: GoodSync-Encrypt.bat
REM Author: Raul Cano Argamasilla
REM Email: raul.cano.argamasilla@gmail.com
REM Date: 14.10.2013
REM
REM Requirements:
REM   GoodSync (Windows version)
REM   AxCrypt (Windows version)
REM	 
REM Description: 
REM This is a script to be used by GoodSync in order to keep a remote encrypted repository of 
REM ALL the files in a local directory. The synchronization is kept between
REM the local files (not encrypted) and the remote copies (encrypted).
REM The concept is easy but can be tricky:
REM - The user synchronizes his local files with a remote repository (e.g. a cloud server, network drive)
REM - The files in the remote repo will be only encrypted files, so we can use a third party provider
REM   and forget about any concerns on privacy.
REM - If another user wants to use the same files from that repo, the system will keep in sync even
REM   with the encrypted files in the remote repo.
REM - The remote repo can serve, therefore, as a backup or middle repository, ALWAYS KEEPING PRIVACY.
REM - If different users want to use the same repository, they will have to use the same encrypting key.
REM
REM Typical use case:
REM 1.The user creates a job to be synced with a cloud repository (or another folder, whatever).
REM 2.Everytime the job is run, all the files on that folder are automatically encrypted and the 
REM   originals are deleted temporarily, leaving the encrypted versions only in the local directory.
REM 3.The analysis and comparison of versions is done among only the encrypted files in both sides(L REM   and R).
REM 4a.If changes are detected, the corresponding files will be synced (either uploaded or downloaded)  
REM 4b.If no changes are detected, nothing happens.
REM 5.Finally, the local files are decrypted back in the local directory, leaving only plain
REM   unencrypted files there (no encrypted files will remain at this point).
REM
REM Note: We decided to encrypt every single file every time the job is called.
REM If we only encrypted the recently changed files the files that are not encrypted in 
REM this step remain unencrypted in the directory and are synced via GoodSync as plain format,
REM something we don't want. For sure there are more elegant ways to approach that but they are
REM out of scope.
REM
REM Usage in GoodSync:
REM Note: The usage must be coherent in all the command lines. That is to say, the passphrase,
REM directory and recursion parameter (-m) must equal for Pre-Analysis, Post-Analysis and Post-Sync.
REM Therefore, within the Automation section of a job, add the following commands.
REM
REM Pre Analysis:
REM [Route_to_script\]GoodSync-Encrypt.bat PA "[my_passphrase]" "[my_directory]" [-m]
REM Post Analysis with no changes:
REM [Route_to_script\]GoodSync-Encrypt.bat PS "[my_passphrase]" "[my_directory]" [-m]
REM Post Sync:
REM [Route_to_script\]GoodSync-Encrypt.bat PS "[my_passphrase]" "[my_directory]" [-m]
REM 
REM
REM Usage in command line:
REM GoodSync-Encrypt.bat <phase> <pass> <dir> <recursive>
REM   <phase> (%1) is the GoodSync phase. Either PA (PreAnalysis, for encryption) or PS (PostSync, for
REM                decryption)
REM   <pass> (%2) is the encryption passphrase
REM   <dir> (%3) is the root folder where the encryption has to start. Do not add trailing slash!
REM   <recursive> (%4) can be -m or empty. If -m , then the encryption applies to all the subdirectories
REM Examples:
REM   GoodSync-Encrypt.bat PA test "test axcrypt" -m
REM   GoodSync-Encrypt.bat PS test "test axcrypt" -m 
REM   GoodSync-Encrypt.bat PA test "test axcrypt"
REM   GoodSync-Encrypt.bat PA "test password with blank spaces" "test axcrypt"
REM   GoodSync-Encrypt.bat PA "passwordNoSpacesAndInsideQuotes" "test axcrypt"
REM
REM ***************************************************************************

REM Check parameters
SETLOCAL
REM Check correct number of arguments
SET arg_count=0
FOR %%x IN (%*) do SET /A arg_count+=1
SET arg_check=false
IF "%arg_count%"=="3" SET arg_check=true
IF "%arg_count%"=="4" SET arg_check=true
IF "%arg_check%" == "false" (
	ECHO Wrong number of arguments. Use:
	ECHO GoodSync-Encrypt.bat [phase] [pass] [dir] [recursive]
	ECHO   [phase]: is the GoodSync phase. Either PA -PreAnalysis, for encryption- or PS -PostSync, for
	ECHO                decryption-
	ECHO   [pass]: is the encryption passphrase
	ECHO   [dir]: is the root folder where the encryption has to start. Do not add trailing slash!
	ECHO   [recursive]: can be -m or empty. If -m , then the encryption applies to all the subdirectories
	ECHO Examples:
	ECHO   GoodSync-Encrypt.bat PA test "test axcrypt dir" -m
	ECHO   GoodSync-Encrypt.bat PS test "test axcrypt dir" -m 
	ECHO   GoodSync-Encrypt.bat PA test "test axcrypt dir"
	ECHO   GoodSync-Encrypt.bat PA "test password with blank spaces" "my/directory/here"
	ECHO   GoodSync-Encrypt.bat PA "passwordNoSpacesAndInsideQuotes" "my/directory/here"
	EXIT /b
)


REM Check the arguments "phase" and "recursive"
SET arg_check=false
IF "%1"=="PA" SET arg_check=true
IF "%1"=="PS" SET arg_check=true

IF "%arg_check%" == "false" (
	ECHO Wrong first parameter. Use one of the following:
	ECHO   PA: Pre Analysis, for encryption
	ECHO   PS: Post Sync, for decryption
	EXIT /b
)

SET arg_check=false
IF "%4"=="-m" SET arg_check=true
IF "%4"=="" SET arg_check=true
IF "%arg_check%" == "false" (
	ECHO Wrong fourth parameter. Use one of the following:
	ECHO   -m: Recursive encription/decryption within the directory
	ECHO   [empty]: Encryption/decryption only in the current directory
	EXIT /b
)

REM Path to the AxCrypt executable file. It may be necessary to write the full path
SET axcrypt=AxCrypt.exe

IF "%1" == "PA" (
	REM To be executed in the "Pre-Analyze" step

	REM Encrypt the files with the given passphrase <pass>, but do not remember this passphrase
	REM This removes the original file and leaves the encrypted version only. After the syncronization
	REM the files are decrypted back to the local system. 
	REM See the "PS" part of this script

	%axcrypt% -b 2 -e -k %2 %4 -z %3\*
	REM Rename all just encrypted files to anonymous names
	REM %axcrypt% %4 -h %3\*.axx

) ELSE (
	REM To be executed in the "Post-Sync" and "Post-Analysis with no changes" step
	IF "%1" == "PS" (
		REM Decrypt all the encrypted files in the directory and clear the cache
		%axcrypt% -b 2 %4 -f -d %3\*.axx -t 
		REM Request that the resident process ends itself, and exits
		%axcrypt% -x
	)
)

ENDLOCAL

REM ---IMPORTANT!---
REM Important to avoid the _gsdata_ directory

REM The rename should do a hash of the original name, not a totally random one, otherwise
REM even if a file is not changed, it will be considered as a new one by GoodSync and unnecessary sync'd

REM Check if the PostSync changes will trigger an OnChange event
REM ---IMPORTANT!---

PAUSE