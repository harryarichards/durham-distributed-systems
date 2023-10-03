import time
import os
import Pyro4
import serpent


def upload_file(frontend):
    # If there is a connected/running server to upload the file to.
    if len(frontend.connected_servers()) != 0:
        # User inputs the name of the file they wish to upload.
        file_name = input('Input the name of the file you wish to upload: ')
        # If the file exists (and is present in the directory).
        if os.path.isfile(file_name):
            # The user is asked if they wish to upload with high reliability.
            high_reliability = input('Upload with high reliability? (Input YES for high reliability).').upper()
            # There choice is noted.
            if high_reliability == 'YES':
                high_reliability = True
            else:
                high_reliability = False
            start_time = time.time()
            # The size of the file is acquired.
            file_size = os.path.getsize(file_name)
            # The reliability of the upload and file size are used to start the upload.
            # The upload is started by deciding how many servers to upload to and creating the
            # file on the server side.
            frontend.start_upld(high_reliability, file_name, file_size)
            bytes_sent = 0
            # We read the file we're uploading.
            with open(file_name, 'rb') as f:
                # We read and send up to 1024 bytes.
                bytes_to_send = f.read(1024)
                # Pass the bytes to the frontend where they can be passed to the
                # server and writtend to the file.
                frontend.upld_file(bytes_to_send)
                # Increase the bytes sent by the number of bytes sent.
                bytes_sent += len(bytes_to_send)
                # Output a statement saying what the % of the upload has been completed.
                if file_size != 0:
                    print('UPLOAD ' + str(round(bytes_sent * 100 / file_size, 2)) + '% COMPLETE')
                # While we still have bytes to send we repeat the above process of reading
                # and sending bytes, keeping track of the % complete.
                while bytes_sent < file_size:
                    bytes_to_send = f.read(1024)
                    frontend.upld_file(bytes_to_send)
                    bytes_sent += len(bytes_to_send)
                    print('UPLOAD ' + str(round(bytes_sent * 100 / file_size, 2)) + '% COMPLETE')
            process_time = time.time() - start_time
            # Output a statement evaluating the success of the upload.
            print('UPLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(bytes_sent) +
                  ' bytes transferred of ' + str(file_size) + ' bytes.')

        else:
            print('The filename provided is not a valid file.')
    else:
        # Otherwise explain to user no servers are currently running.
        print('UNABLE TO UPLOAD FILE CURRENTLY: servers not currently running.')

def list_directory_contents(frontend):
    # If there is a connected/running server to list the file(s) of.
    if len(frontend.connected_servers()) != 0:
        # Get the contents fo the server directory from the frontend and present it to the user.
        dir_list = frontend.list_directory_contents()
        print()
        print('SERVER DIRECTORY CONTAINS: ')
        print()
        for filename in dir_list:
            print(filename)
    else:
        # Otherwise explain to user no servers are currently running.
        print('UNABLE TO LIST FILES: no server(s) not currently running.')

def download_file(frontend):
    # If there is a connected/running server to download the file from.
    if len(frontend.connected_servers()) != 0:
        # Receive the name of the file we wish to download.
        file_name = input('Input the name of the file you wish to download: ')
        # Acquite the size of the file name we wish to download.
        file_size = frontend.start_dwld(file_name)
        # If the file size is not -1 it is present on the server, do the following.
        if file_size != -1:
            start_time = time.time()
            # We create a file with the name of the file we're downloading.
            with open(file_name, 'wb') as downloaded_file:
                num_bytes_received = 0
                # While we are still receiving bytes.
                while num_bytes_received < file_size:
                    # Obtain the bytes we're receiving from the frontend.
                    bytes_received = frontend.dwld_file(file_name, file_size)
                    # Convert them back to bytes (as Pyro encodes them when transferring them).
                    bytes_received = serpent.tobytes(bytes_received)
                    # Increase the number of bytes received by the number of bytes we just received.
                    num_bytes_received += len(bytes_received)
                    # Write the bytes we received to the file we've created.
                    downloaded_file.write(bytes_received)
                    # Ouput the progress of the download.
                    print('DOWNLOAD ' + str(round(num_bytes_received * 100 / file_size, 2)) + '% COMPLETE')
            process_time = time.time() - start_time
            # Output a summary of how the download went.
            print('DOWNLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(
                num_bytes_received) + ' bytes received of ' + str(file_size) + ' bytes.')
        else:
            # If the file size is -1 inform the user it does not exist.
            print('FILE STATED DOES NOT EXIST.')
    else:
        # Otherwise explain to user no servers are currently running.
        print('UNABLE TO DOWNLOAD FILE CURRENTLY: no server(s) not currently running.')

def delete_file(frontend):
    # If there is a connected/running server to delete the file from.
    if len(frontend.connected_servers()) != 0:
        # Receive the name of the file the user wishes to delete.
        file_name = input('Input the name of the file you wish to delete: ')
        # Get the entire contents of the server directories (for all running servers).
        directory_contents = frontend.list_directory_contents()
        # If the file isn't present on the server, let the user know.
        if file_name not in directory_contents:
            print('FILE NOT PRESENT.')
        else:
            # If the file is present on the server, ask the user to confirm they wish to delete it.
            confirm = input('Please confirm you wish to delete the file, input Yes to delete, input No to cancel.')
            # If they wish to delete it proceed with the delete otherwise, abandon the delete.
            if confirm.upper() == 'YES':
                frontend.delete_file(file_name)
                print('FILE DELETED.')
            elif confirm.upper() == 'NO':
                print('Delete abandoned by the user!')
            else:
                print('Input not valid: Delete abandoned by the user!')
    else:
        # Otherwise explain to user no servers are currently running.
        print('UNABLE TO DELETE FILE CURRENTLY: no server(s) not currently running.')


def quit():
    # Exit the program.
    print('QUIT EXECUTED: SESSION CLOSED.')
    exit()


def prompt():
    # Initialise the frontend as None.
    frontend = None
    # Repeat this.
    while True:
        print()
        # Ask the user for input.
        operation = input('Input the operation you wish to perform (CONN, UPLD, LIST, DWLD, DELF, QUIT): ')
        # If the operation is of length 4.
        if len(operation) == 4:
            if operation == 'CONN':
                # If the user wishes to connect the set frontend as the Pyro object
                #  associated with frontend.name in the nameserver.
                frontend = Pyro4.Proxy('PYRONAME:frontend.name')
                try:
                    frontend._pyroBind()
                except:
                    print('Frontend unreachable, run frontend.py so we may access relevant methods.')
            # The rest is fairly explanatory, calling the relevant function for an operation
            # if the connection is initialised and informing the user to initialise a connection
            # if they haven't.
            # We try ._pyroBind() as if this cannot happen we know that the frontend is not initialised.
            elif operation == 'UPLD':
                try:
                    frontend._pyroBind()
                    upload_file(frontend)
                except:
                    print('A connection must be initialised before inputting other operations.')
                    print('INPUT CONN to initialise a connection.')
            elif operation == 'LIST':
                try:
                    frontend._pyroBind()
                    list_directory_contents(frontend)
                except:
                    print('A connection must be initialised before inputting other operations.')
                    print('INPUT CONN to initialise a connection.')
            elif operation == 'DWLD':
                try:
                    frontend._pyroBind()
                    download_file(frontend)
                except:
                    print('A connection must be initialised before inputting other operations.')
                    print('INPUT CONN to initialise a connection.')
            elif operation == 'DELF':
                try:
                    frontend._pyroBind()
                    delete_file(frontend)
                except:
                    print('A connection must be initialised before inputting other operations.')
                    print('INPUT CONN to initialise a connection.')
            elif operation == 'QUIT':
                quit()
            else:
                print('The operation you inputted is not valid.')
        else:
            # If the operation is not of length 4 then it is invalid.
            print('The operation you inputted is not valid.')


if __name__ == '__main__':
    # When the program starts call the prompt function.
    prompt()