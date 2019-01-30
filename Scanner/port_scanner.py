#!../venv/bin/python3
#!--*--coding:utf-8--*--
__author__ = 'Cazin Christophe'

''' 
Role :  Create a script to scan hosts/ a LAN in selecting port /& range of ports 
        I have created a program who create queue and thread to launch tasks
        All params are put in the queue 
        The queue is treated by X instances of threads to accelerate the scan
        Script has been done especially for PWK test to help me to understand how to hack / scan ... servers 
        and perhaps win time for the test. 
    
        
Next Feature :  I am going to include the next actions regarding a specific port 
                do action 
                For instance, an HTTP server, take the banner an provide informations 
                to accelerate the resolution to hack this port on this server
                ( to avoid a HTTP hidden on an exotic port number )

If you would like to use this script, no problem but you have ti understand how it work. 
It the goal of this script.

'''

# Declaration part ####################################################################
import socket
import argparse, textwrap
#import os, sys
import threading
import queue
import time
import re

NUMBER_OF_THREADS = 20
timeout_threads = 0.1
portlist = range(1024)
port_param_max = 1025
port_status = {
    True: 'OPEN',
    False: 'CLOSED'
}
commom_ports = {
    21:  "ftp",
    22:  "ssh",
    23:  "telnet",
    25:  "smtp",
    53:  "dns",
    80:  "http",
    110: "pop3",
    139: "netb",
    443: "https",
    445: "ms-ds",
}
port_queue = queue.Queue()  # Create a Queue object
result_dic = {} # Store all scan result: char host, int port, bool opened

tmess_dic = {
    'I': "Inf",
    'E': "Err",
    'W': "War"
} # Store type of message for print_message def

# Function part ####################################################################
def get_args():
    """ Treate / get / parse arguments
        And return host/network , port/list of ports , open
    """
    global fl_verbose # Flag argument verbose to be used by all program
    # Get/Check/Parse args
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent('''\
        Script who scan port for a host or a list of hosts and more ...
        Using for PWK OSCP exam
        '''))
    # Add either -net or -target but one is required
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-target", "-t", metavar="host", type=str, nargs='+',
                       help="one or more target hostnames or IP adresses to scan. e.g : -t 10.0.0.2,localhost ")
    group.add_argument("-net", "-n", metavar="net", type=str,nargs='+',
                       help="network e.g: -net 10.11.1.0/24 ")
    parser.add_argument('-port', '-p', metavar='p', required=True, type=str, nargs='+',
                        help="list of port and/or range ( -p 1,80,100,105-120)")
    parser.add_argument('--open', action='store_true',
                        help="Only show open (or possibly open) ports")
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    # Treate args
    port_l = list()
    host_l = list()
    fl_verbose = True if args.verbose else False
    # Treate port args: -port
    for p in args.port[0].split(","):
        p_r = re.search(r'^[0-9]{1,4}\-[0-9]{1,4}$', p)
        if p_r:
            p_min, p_max = p.split("-")
            for r in range(int(p_min), int(p_max)+1):
                port_l.append(r)
        elif re.search(r'^[0-9]{1,4}$', p) and int(p) < port_param_max:
            port_l.append(int(p))
        else:
            print_message("Param ( {} ) not taken into account. Port Max {}".format(p, port_param_max),
                          'E')

    port_l=sorted(list(set(port_l))) # Convert list to set to delete duplicate values and sort
    # Treate net and target args: -target and -net
    if args.net:
        # Split a network to a list of IPs
        for net_field in args.net[0].split(","):

            n, m = net_field.split("/")
            if m != '24':
                print_message("Error : param ( {}/{} ) not taken into account".format(n,m), 'E')
                print_message("Only 24 mask is implemented", 'E')
            else:
                n_r = re.search(r'^([0-9]{1,3}\.){3}', n)
                if n_r:
                    for r in range(1, 255):
                        host_l.append(n_r.group(0) + str(r))
                    host_l = list(set(host_l)) # Convert list to set to delete duplicate values

                    return host_l, port_l, args.open
                else:
                    print_message("Error : Bad network ( {}/{} ) not taken into account.".format(n,m), 'E')
    elif args.target:
        for h in args.target[0].split(","):
            # Check pattern in the host 1-25 chars with . allowed
            if re.search(r'^[A-Za-z0-9.]{1,25}$', h):
                host_l.append(h)
            else:
                print_message("Error : Host ( {} ) not taken into account.".format(h), 'E')
        host_l = list(set(host_l))  # Convert list to set to delete duplicate values

        return host_l, port_l, args.open
    return None, None, None



def is_port_open(host, port):
    """ Open socket for host,port association
        TCP Full connect

        :param host: Hostname/IP
        :param port: port
        :type host: str
        :type port: str
        :return: True/False if the port is opened
    """
    try:
        sock = socket.socket()              # Create a socket object
        sock.settimeout(timeout_threads)    # Set parameters on this object
        sock.connect((host, int(port)))     # TCP full connect
        sock.close()                        # Close the socket
    except socket.error:
        return False  # port not open
    return True  # port open



def scanner_worker_thread():
    """ Launch function is_port_open in get port number in the queue
        what I want to launch in my thread """
    while True:
        host, port = port_queue.get()  # Get the next (host,port) in the queue
        print_message("Get {} {} in the queue".format(host, port), 'I') if fl_verbose else None
        if is_port_open(host, port):
            result_dic[host, port]= True
        else:
            result_dic[host, port]= False
        port_queue.task_done()  # After a get in the queue to validate and consume


def print_result(r_dic):
    """ Print and order the content of result dictionnary
        Print only regarding some params

    :param r_dic: Content of dictionnary {(str host,int port), bool status_port}
    :return: None
    """
    for (host, port), opened in sorted(r_dic.items()):
        port_t = "({:7s})".format(commom_ports[port]) if port in commom_ports else ""
        if opened or ( not opened and not fl_port_open ):
            print("{:15s}/{:4d} {:6s} {:6s}".format(host, port, port_t, port_status[opened]))

def print_message(message, type):
    """
    Print information message with different type in a specific format
    [I]: Information
    [E]: Error
    [W]: Warning

    :param message: Message to print
    :param type: Type of message
    :return: None
    """
    print("[{:3s}] {}".format(tmess_dic[type],message))


# Main ###############################################################################
time_consumed = {}
time_consumed['start_time'] = time.time() # Register time to measure the time of treatement

# Get arguments in each list
host_list, port_list , fl_port_open = get_args()
# Only if the params are returned
if host_list and port_list:

    # Create thread for each is_port_open
    for t_n in range(NUMBER_OF_THREADS):
        # Creation of thread can be done with args or kwargs
        t = threading.Thread(target=scanner_worker_thread)
        t.daemon = True
        t.start()
        print_message("Thread {} created".format(t_n), 'I') if fl_verbose else None # Print only if verbose flag

    for h in host_list:
        for p in port_list:
            port_queue.put((h, p))  # Fill the queue with tuple (host,port)
            print_message("Put {} {} in the queue".format(h,p), 'I') if fl_verbose else None
    port_queue.join()  # Waiting for all threads are terminated. Timeout in second
    print_result(result_dic)

time_consumed['time_end'] = time.time()
print("Done. Scanning took {:5.2f} sec".format(time_consumed['time_end'] - time_consumed['start_time']))
