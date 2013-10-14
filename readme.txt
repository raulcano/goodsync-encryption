Script Name: GoodSync-Encrypt-Decrypt.bat
Author: Raul Cano Argamasilla
Email: raul.cano.argamasilla@gmail.com
Date: 14.10.2013

Requirements:
  GoodSync (Windows version)
  AxCrypt (Windows version)
	 
Description: 
This is a script to be used by GoodSync in order to keep a remote encrypted repository of 
ALL the files in a local directory. The synchronization is kept between
the local files (not encrypted) and the remote copies (encrypted).
The concept is easy but can be tricky:
- The user synchronizes his local files with a remote repository (e.g. a cloud server, network drive)
- The files in the remote repo will be only encrypted files, so we can use a third party provider
  and forget about any concerns on privacy.
- If another user wants to use the same files from that repo, the system will keep in sync even
  with the encrypted files in the remote repo.
- The remote repo can serve, therefore, as a backup or middle repository, ALWAYS KEEPING PRIVACY.
- If different users want to use the same repository, they will have to use the same encrypting key.

Typical use case:
1.The user creates a job to be synced with a cloud repository (or another folder, whatever).
2.Everytime the job is run, all the files on that folder are automatically encrypted and the 
  originals are deleted temporarily, leaving the encrypted versions only in the local directory.
3.The analysis and comparison of versions is done among only the encrypted files in both sides(L   and R).
4a.If changes are detected, the corresponding files will be synced (either uploaded or downloaded)  
4b.If no changes are detected, nothing happens.
5.Finally, the local files are decrypted back in the local directory, leaving only plain
  unencrypted files there (no encrypted files will remain at this point).

Note: We decided to encrypt every single file every time the job is called.
If we only encrypted the recently changed files the files that are not encrypted in 
this step remain unencrypted in the directory and are synced via GoodSync as plain format,
something we don't want. For sure there are more elegant ways to approach that but they are
out of scope.

Usage in GoodSync:
Note: The usage must be coherent in all the command lines. That is to say, the passphrase,
directory and recursion parameter (-m) must equal for Pre-Analysis, Post-Analysis and Post-Sync.
Therefore, within the Automation section of a job, add the following commands.

Pre Analysis:
[Route_to_script\]GoodSync-Encrypt-Decrypt.bat PA "[my_passphrase]" "[my_directory]" [-m]
Post Analysis with no changes:
[Route_to_script\]GoodSync-Encrypt-Decrypt.bat PS "[my_passphrase]" "[my_directory]" [-m]
Post Sync:
[Route_to_script\]GoodSync-Encrypt-Decrypt.bat PS "[my_passphrase]" "[my_directory]" [-m]


Usage in command line:
GoodSync-Encrypt-Decrypt.bat <phase> <pass> <dir> <recursive>
  <phase> (%1) is the GoodSync phase. Either PA (PreAnalysis, for encryption) or PS (PostSync, for
               decryption)
  <pass> (%2) is the encryption passphrase
  <dir> (%3) is the root folder where the encryption has to start. Do not add trailing slash!
  <recursive> (%4) can be -m or empty. If -m , then the encryption applies to all the subdirectories
Examples:
  GoodSync-Encrypt-Decrypt.bat PA test "test axcrypt" -m
  GoodSync-Encrypt-Decrypt.bat PS test "test axcrypt" -m 
  GoodSync-Encrypt-Decrypt.bat PA test "test axcrypt"
  GoodSync-Encrypt-Decrypt.bat PA "test password with blank spaces" "test axcrypt"
  GoodSync-Encrypt-Decrypt.bat PA "passwordNoSpacesAndInsideQuotes" "test axcrypt"