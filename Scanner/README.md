## port_scanner.py

## Role :  
        Create a script to scan hosts/ a LAN in selecting port or/and range of ports
        I have created a program who create queue and thread to launch tasks
        All params are put in the queue 
        The queue is treated by X instances of threads to accelerate the scan
        Script has been done especially for PWK test to help me to understand how to hack / scan ... servers 
        and perhaps win time for the test. 
        Using for PWK OSCP exam

## usage: 
        port_scanner.py [-h] (-target host[,host, ...] | -net[,net,...])
                       -port p[,p...] [--open] [--verbose]

        optional arguments:
        -h, --help            show this help message and exit
        -target host [host ...], -t host [host ...]     one or more target hostnames or IP adresses to scan.
        -net net,[net ...], -n net [net ...]            # list of networks ( -net 192.168.1.0/24,10.0.0.0/24 )
        -port p,[p ...], -p p [p ...]                   # list of port and/or range ( -p 1,80,100,105-120)
        --open                Only show open (or possibly open) ports
        --verbose, -v         Verbose mode
##
        e.g : ./port_scanner.py -target 192.168.1.127,localhost,kali -port 21,22,80,440-500 --open
        ./port_scanner.py -target 192.168.1.0/24,10.0.0.1/24 -port 21,22,80,440-500 --open -v

    
In Progress : Include banner grabbing

If you would like to use this script, no problem but you have to understand how it work.
It the goal of this script.
