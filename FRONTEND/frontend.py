import Pyro4


# Set the servers to the Pyro objects associated with there logical names in the name server.
server1 = Pyro4.Proxy('PYRONAME:server.server1')
server2 = Pyro4.Proxy('PYRONAME:server.server2')
server3 = Pyro4.Proxy('PYRONAME:server.server3')
# Put the servers in a list.
servers = [server1, server2, server3]


# Expose this entire class so we may allow the client to use its functions.
@Pyro4.expose
class Frontend(object):
    def __init__(self):
        # Initialise the upload servers to a blank list
        self.upload_servers = []
        # Initialise the number of disconnected servers to 0.
        self.num_disconnected_servers = 0

    def connected_servers(self):
        connected_servers = []
        self.num_disconnected_servers = 0
        # For each of our 3 servers.
        for server in servers:
            try:
                # If we're able to check the connection of the server the server connection is there.
                if server.check_connection:
                    # thus we add it to connected servers.
                    connected_servers.append(server)
            except:
                # If we're unable to we increase the number of disconnected servers by 1.
                self.num_disconnected_servers += 1
        # We return the list of connected servers.
        return connected_servers


    def start_upld(self, high_reliability, file_name, file_size):
        # Reset the upload servers to blank.
        self.upload_servers = []
        # Obtain a list of the currently connected/running servers.
        connected_servers = self.connected_servers()
        # If there are connected servers.
        if len(connected_servers) != 0:
            # If the reliability is high.
            if high_reliability:
                # Add all connected servers to the upload servers.
                for server in connected_servers:
                    self.upload_servers.append(server)
            else:
                # If the reliability is not high, add the server with the least files
                # to the upload servers.
                least_files = len(connected_servers[0].list_directory_contents())
                upload_server = connected_servers[0]
                for server in connected_servers:
                    if  len(server.list_directory_contents()) < least_files:
                        least_files = len(server.list_directory_contents())
                        upload_server = server
                self.upload_servers.append(upload_server)
            for upload_server in self.upload_servers:
                upload_server.start_upload_file(file_name, file_size)
        else:
            # If there are no servers to upload to, print this.
            print('Currently no servers to upload to.')


    def upld_file(self, bytes_received):
        # For each server in the upload servers.
        for upload_server in self.upload_servers:
            # Pass the bytes that were received to the server where they can be wrote to the file.
            upload_server.upload_file(bytes_received)


    def list_directory_contents(self):
        directory_contents = []
        # Obtain a list of the currently connected/running servers.
        connected_servers = self.connected_servers()
        # For each currently connected server.
        for server in connected_servers:
            # Obtain the contents of that servers directory.
            server_directory_contents = server.list_directory_contents()
            # For each file in the directory not currently in the list add it to the list
            for file in server_directory_contents:
                if file not in directory_contents:
                    directory_contents.append(file)
        # Return the directory contents of all the running servers.
        return directory_contents


    def start_dwld(self, file_name):
        # Obtains a list of the directory contents of all running servers.
        server_contents = self.list_directory_contents()
        # Obtains a list of all running servers.
        connected_servers = self.connected_servers()
        # If the file name input is in the directory contents.
        if file_name in server_contents:
            # Pick the first server that contains the file to download it from.
            for server in connected_servers:
                if file_name in server.list_directory_contents():
                    self.download_server = server
                    break
        else:
            # Return -1 to indicate the file input is not present.
            return -1
        # Return the size of the file the user wishes to download.
        return self.download_server.start_download_file(file_name)


    def dwld_file(self, file_name, file_size):
        # Return up to 1024 bytes of the file we wish to download (this function is called
        # iteratively until we have downloaded the entire file).
        return self.download_server.download_file(file_name, file_size)


    def delete_file(self, file_name):
        # Obtains a list of all running servers.
        connected_servers = self.connected_servers()
        # For each running server.
        for server in connected_servers:
            # If the server contains the file we wish to delete.
            server_directory_contents = server.list_directory_contents()
            if file_name in server_directory_contents:
                # Delete the file fromt he servers directory.
                server.delete_file(file_name)


if __name__ == '__main__':
    # As soon as we run the program.
    # Creates a Pyro4 Daemon which dispatched remote method calls to the appropriate objects.
    frontend = Pyro4.Daemon()
    # Finds the name server, a server relating logical names and pyro objects.
    ns = Pyro4.locateNS()
    # Registers the Pyro object (Daemon) under a given id.
    uri = frontend.register(Frontend)
    # Registers a logical name with this id for the pyro object in the name server.
    ns.register('frontend.name', uri)
    # Goes in a loop to service incoming requests.
    frontend.requestLoop()