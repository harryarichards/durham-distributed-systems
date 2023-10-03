import os
import Pyro4
import serpent

@Pyro4.expose
class Server(object):
    def __init__(self):
        # Initially.
        # Set number of received bytes to 0.
        self.current_num_received_bytes = 0
        # Set number of sent bytes to 0.
        self.current_num_sent_bytes = 0
        # Set upload file size to 0.
        self.upload_file_size = 0
        # Set current file to None.
        self.current_file = None

    def check_connection(self):
        # If we are able to check the connection return true as this means the connection is there.
        return True

    def start_upload_file(self, file_name, file_size):
        # Try the following.
        try:
            # Set the number of received bytes to 0.
            self.current_num_received_bytes = 0
            # Open a file to which we will write binary that has the name of the file we are
            # uploading.
            self.current_file = open(os.getcwd() + '/SERVER FILES/' + file_name, 'wb')
            # Set the upload file size to the file size passed in.
            self.upload_file_size = file_size

        except:
            # If we were unable to do the above print accordingly.
            print('UPLOAD FAILED.')

    def upload_file(self, received_bytes):
        # Set the received bytes to their decoded version (as Pyro encodes them when passing them
        # around).
        received_bytes = serpent.tobytes(received_bytes)
        # Increased the received bytes by the number of bytes we just received.
        self.current_num_received_bytes += len(received_bytes)
        # Write the received bytes to the we created in start upload.
        self.current_file.write(received_bytes)
        # If the have uploaded all of the bytes (wrote them to the new file).
        if self.current_num_received_bytes == self.upload_file_size:
            # Close the file we uploaded.
            self.current_file.close()
            # Print accordingly.
            print('UPLOAD COMPLETE.')


    def list_directory_contents(self):
        # Obtain a list of the files in the servers 'SERVER FILES' directory.
        dir_list = [file for file in os.listdir(os.getcwd() + '/SERVER FILES')
                    if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file)]
        # Exclude any hidden files.
        dir_list = [file for file in dir_list if not file.startswith('.')]
        # Print that we have just obtained the contents of the directory.
        print('DIRECTORY CONTENTS OBTAINED.')
        # Return the list of the contents of the directory.
        return dir_list

    def start_download_file(self, file_name):
        # Set the number of bytes sent to 0.
        self.current_num_sent_bytes = 0
        # If the file is present in the server files directory.
        if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file_name):
            # Obtain the file size of said file.
            file_size = os.path.getsize(os.getcwd() + '/SERVER FILES/' + file_name)
            # Open the file.
            self.current_file = open(os.getcwd() + '/SERVER FILES/' + file_name, 'rb')
            #Return the file size.
            return file_size
        # If the file does not exist return -1.
        return -1

    def download_file(self, file_name, file_size):
        # If the file is present in the server files directory.
        if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file_name):
            # If the number of bytes sent is not yet the same as the file size.
            if self.current_num_sent_bytes != file_size:
                # Read up to 1024 new bytes from the current file.
                bytes_to_send = self.current_file.read(1024)
                # Increase the number of bytes sent by the number of bytes we just read.
                self.current_num_sent_bytes += len(bytes_to_send)
                # Return the bytes we just read.
                return bytes_to_send
            else:
                # Otherwise reset the number of bytes sent to 0 and output the download is complete.
                self.current_num_sent_bytes = 0
                print('DOWNLOAD COMPLETE.')
        else:
            # If the file does not exist print a statement accordingly.
            print('DOWNLOAD FAILED.')


    def delete_file(self, file_name):
        # If the file is present in the server files directory.
        if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file_name):
            # Delete the file and print a statement accordingly.
            os.remove(os.getcwd() + '/SERVER FILES/' + file_name)
            print('FILE DELETED.')

if __name__ == '__main__':
    # As soon as we run the program.
    # Creates a Pyro4 Daemon which dispatched remote method calls to the appropriate objects.
    server2 = Pyro4.Daemon()
    # Finds the name server, a server relating logical names and pyro objects.
    ns = Pyro4.locateNS()
    # Registers the Pyro object (Daemon) under a given id.
    uri = server2.register(Server)
    # Registers a logical name with this id for the pyro object in the name server.
    ns.register('server.server2', uri)
    # Goes in a loop to service incoming requests.
    server2.requestLoop()
