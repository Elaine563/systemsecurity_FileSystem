# SystemSecurity_FileSystem
CSCI262 Assignment 1 PART 2 - FileSystem

What it does

Register users with salted MD5 password hashing
Log in with authentication
Create/Read/Write/Append files with Bell-LaPadula access control
4 security levels: 0 (Unclassified) → 3 (Top Secret)


How to run

Register a user first:

python FileSystem.py -i

Then login:

python FileSystem.py

Menu options


C - Create file
R - Read file
W - Write to file
A - Append to file
L - List all files
S - Save
E - Exit


Bell-LaPadula rules


Read: your clearance must be >= file level (no reading up)
Write: your clearance must be <= file level (no writing down)


Requirements
Python 3
No extra libraries needed
