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

NUMBER_OF_THREADS = 30
timeout_threads = 0.1
portlist = range(1024)
commom_ports = {
    21:  "ftp",
    22:  "ssh",
    23:  "telnet",
    25:  "smtp",
    53:  "dns",
    80:  "http",
    110: "pop3",
    139: "netbios",
    443: "https",
    445: "microsoft-ds",
}# host = sys.argv[1]
port_queue = queue.Queue()  # Create a Queue object


# Function part ####################################################################
def get_args():
    """ Treate / get / parse arguments
        And return host/network , port/list of ports , open
    """
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
    # parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    # Treate args
    port_l = list()
    host_l = list()
    # Treate port args: -port
    for p in args.port[0].split(","):
        p_r = re.search(r'^[0-9]{1,4}\-[0-9]{1,4}$', p)
        if p_r:
            p_min, p_max = p.split("-")
            for r in range(int(p_min), int(p_max)+1):
                port_l.append(r)
        elif re.search(r'^[0-9]{1,4}$', p) and int(p) < 1025:
            port_l.append(int(p))
        else:
            print("Error : param {} not taken into account".format(p))
    port_l=sorted(list(set(port_l))) # Convert list to set to delete duplicate values and sort
    # Treate net and target args: -target and -net
    if args.net:
        # Split a network to a list of IPs
        for net_field in args.net[0].split(","):
            n, m = net_field.split("/")
            if m != '24':
                print("Error : param {}/{} not taken into account. Only 24 mask is allowed for the moment".format(n,m))
            else:
                n_r = re.search(r'^([0-9]{1,3}\.){3}', n)
                if n_r:
                    for r in range(1, 255):
                        host_l.append(n_r[0] + str(r))
                    host_l = list(set(host_l)) # Convert list to set to delete duplicate values

                    return host_l, port_l, args.open
                else:
                    print("Error : Bad network {}/{} not taken into account.")
    elif args.target:
        for h in args.target[0].split(","):
            # Check pattern in the host 1-25 chars with . allowed
            if re.search(r'^[A-Za-z0-9.]{1,25}$', h):
                host_l.append(h)
            else:
                print("Error : Host {} not taken into account.".format(h))
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
        sock = socket.socket()
        sock.settimeout(timeout_threads)
        sock.connect((host, int(port)))
        sock.close()
    except socket.error:
        return False  # port not open
    return True  # port open



def scanner_worker_thread():
    """ Launch function is_port_open in get port number in the queue
        what I want to launch in my thread """
    while True:
        host, port = port_queue.get()  # Get the next (host,port) in the queue

        if is_port_open(host, port):
            if port in commom_ports:
                print("{}({}) is OPEN on {}".format(port, commom_ports[port], host))
            else:
                print("{} is OPEN on {}".format(port, host))
        else:
            if not fl_port_open:
                if port in commom_ports:
                    print("{}({}) is CLOSED on {}".format(port, commom_ports[port], host))
                else:
                    print("{} is CLOSED on {}".format(port, host))


        port_queue.task_done()  # After a get in the queue to validate and consume


# Main ###############################################################################
start_time = time.time()

# Get arguments in each list
host_list, port_list , fl_port_open = get_args()
# Only if the params are returned
if host_list and port_list:

    # Create thread for each is_port_open
    for _ in range(NUMBER_OF_THREADS):
        # Creation of thread can be done with args or kwargs
        t = threading.Thread(target=scanner_worker_thread)
        t.daemon = True
        t.start()

    for h in host_list:
        for p in port_list:
            port_queue.put((h, p))  # Fill the queue with tuple (host,port)

    port_queue.join()  # Waiting for all threads are terminated. Timeout in second
end_time = time.time()
print("Done. Scanning took {:5.2f} sec".format(end_time - start_time))
