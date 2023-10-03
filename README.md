In terminal input:
python3 -m Pyro4.naming

Navigate to SERVER1 directory:
python3 server1.py 
(Similarly for server2.py and server3.py.)

Navigate to FRONTEND directory:
python3 frontend.py

Navigate to CLIENT directory:
python3 client.py

Input for operations is case-sensitive.

INPUT CONN to connect
INPUT UPLD to upload a file, any file you wish to upload must be in the same directory as client.py and are uploaded to one of the SERVER FILES subdirectories
	   or all for a high-reliability upload.
INPUT LIST to list files all files in all SERVER FILES subdirectories.
INPUT DWLD to download a file, any file you wish to download must be in a SERVER FILES subdirectory.
INPUT DELF to delete a file, deletes specified file from all SERVER FILES subdirectories.
INPUT QUIT to quit the program.

The server program must be shut down manually, and will continue to run unless you tell it not to.

If no server is running the system will tell you this.
If frontend.py is not running the system will tell you this.



You may quit client and re-connect.