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
    'I': 'Inf',
    'E': 'Err',
    'W': 'War',
    'L': 'Log'
} # Store type of message for print_message def

# Function part ####################################################################
def get_args():
    """ Treate / get / parse arguments
        And return host/network , port/list of ports , open
    """
    global fl_verbose, fl_banner # Flag argument verbose to be used by all program
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
    parser.add_argument('--banner', action='store_true',
                        help="Get banner on the open ports")
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    # --banner need to be used with --open ( not mandatory but better to read )
    parser.error("--banner requires --open argument") if args.banner and not args.open else None

    # Treate args
    port_l = list()
    host_l = list()
    fl_verbose = True if args.verbose else False # Activate the global flag verbose
    fl_banner = True if args.banner else False # Activate the global flag banner


    # Treate port args: -port and load in port_l
    for p in args.port[0].split(","):
        if re.search(r'^[0-9]{1,4}\-[0-9]{1,4}$', p):   # Check if port range
            p_min, p_max = p.split("-")
            for r in range(int(p_min), int(p_max)+1):
                port_l.append(r)
        elif re.search(r'^[0-9]{1,4}$', p) and int(p) < port_param_max: # if port < 1024
            port_l.append(int(p))
        else:
            print_message("Param ( {} ) not taken into account. Port Max {}".format(p, port_param_max),
                          type='W')
    port_l= sorted(list(set(port_l))) if port_l else None # Convert list to set to delete duplicate values and sort

    # Treate net and target args: -target and -net
    if args.net:
        # Split a network to a list of IPs
        for net_field in args.net[0].split(","):
            n, m = re.split(r'/', net_field)
            if m and m != '24':         # only manage this netmask
                print_message("Error : param ( {}/{} ) not taken into account".format(n,m), type='E')
                print_message("Only 24 mask is implemented", type='E')
            elif re.search(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', n):
                for r in range(1, 255):
                    host_l.append(re.search(r'^([0-9]{1,3}\.){3}', n).group(0) + str(r))

               # return host_l, port_l, args.open
            else:
                print_message("Error : Bad network ( {}/{} ) not taken into account.".format(n,m), type='E')
    elif args.target:
        for h in args.target[0].split(","):
            # Check pattern in the host 1-25 chars with . allowed
            if re.search(r'^[A-Za-z0-9._]{1,25}$', h):
                host_l.append(h)
            else:
                print_message("Error : Host ( {} ) not taken into account.".format(h), type='W')
    host_l = list(set(host_l)) if port_l else None  # Convert list to set to delete duplicate values
    return host_l, port_l, args.open



def is_port_open(host, port):
    """ Open socket for host,port association
        TCP Full connect

        :param host: Hostname/IP
        :param port: port
        :type host: str
        :type port: str
        :return: True/False if the port is opened
    """
    content_dic = {}
    try:
        sock = socket.socket()              # Create a socket object
        sock.settimeout(timeout_threads)    # Set parameters on this object
        sock.connect((host, int(port)))     # TCP full connect
        if fl_banner:
            sock.send(b'ViolentPython\r\n')
            content_dic['banner'] = sock.recv(100)  # load content of banner into local dictionnary
        sock.close()                        # Close the socket
        content_dic['opened'] = True  # port open
    except socket.error:
        content_dic['opened']= False # port not open
    return content_dic




def scanner_worker_thread():
    """ Launch function is_port_open in get port number in the queue
        what I want to launch in my thread """
    while True:
        host, port = port_queue.get()  # Get the next (host,port) in the queue
        print_message("Got {} {} in the queue".format(host, port)) if fl_verbose else None
        result_dic[host, port] = is_port_open(host, port)
        port_queue.task_done()  # After a get in the queue to validate and consume


def print_result(r_dic):
    """ Print and order the content of result dictionnary
        Print only regarding some params

    :param r_dic: Content of dictionnary {(str host,int port), bool status_port}
    :return: None
    """
    for (host, port), content_dic, in sorted(r_dic.items()):
        port_t = "({:6s})".format(commom_ports[port]) if port in commom_ports else ""  # Load port known to print

        banner = content_dic.get('banner')  # check in the dict if the 'banner' reference is there for this host/port
        banner_p = str(banner) if banner else ""  # Load a variable to print if banner is not None
        if content_dic['opened'] or ( not content_dic['opened'] and not fl_port_open):
            print_message("{:15s}/{:4d} {:8s} {:6s} {:30s}".format(host, port, port_t,
                                                                   port_status[content_dic['opened']],
                                                                   banner_p), type='L')


def print_message(message, **kwargs ):
    """ Print information message with different type in a specific format
    [I]: Information
    [E]: Error
    [W]: Warning
    [L]: Logging
    if output is selected, all is written into this file
    :param  **kwargs type

    """
    type=kwargs.get('type','I') # Check kwargs type entered if no 'I'
    print("[{:3s}] {}".format(tmess_dic[type],message))


def create_thread():
    """
    Create threads and launch main function scanner_worker_thread
    :return:
    """
    for _ in range(NUMBER_OF_THREADS):
        # Creation of thread
        t = threading.Thread(target=scanner_worker_thread)
        t.daemon = True
        t.start()
    print_message("{} threads created".format(NUMBER_OF_THREADS)) if fl_verbose else None  # Print only if verbose flag

def fill_queue(host_list,port_list):
    for h in host_list:
        for p in port_list:
            port_queue.put((h, p))  # Fill the queue with tuple (host,port)
            print_message("Put {} {} in the queue".format(h, p)) if fl_verbose else None
    port_queue.join()  # Waiting for all threads are terminated. Timeout in second


# Main ###############################################################################
def main():
    global fl_port_open  # Global variable used in others functions
    time_consumed = {}
    time_consumed['start_time'] = time.time() # Register time to measure the time of treatement

    # Get arguments in each list
    host_list, port_list , fl_port_open = get_args()
    # Only if the params are returned
    if host_list and port_list:
        create_thread()
        fill_queue(host_list,port_list)
        print_result(result_dic)
    time_consumed['time_end'] = time.time()

    print_message("Done.")
    print_message("Scanning took {:5.2f} sec".format(time_consumed['time_end'] - time_consumed['start_time']))


if __name__ == '__main__':
    main()