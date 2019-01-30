#!--*--coding:utf-8--*--
usage: port_scanner.py [-h] (-target host [host ...] | -net net [net ...])
                       -port p [p ...] [--open] [--verbose]

Script who scan port for a host or a list of hosts and more ...
Using for PWK OSCP exam

optional arguments:
  -h, --help            show this help message and exit
  -target host [host ...], -t host [host ...]
                        one or more target hostnames or IP adresses to scan.
                        e.g : -t 10.0.0.2,localhost
  -net net,[net ...], -n net [net ...]
                        network e.g: -net 10.11.1.0/24
  -port p,[p ...], -p p [p ...]
                        list of port and/or range ( -p 1,80,100,105-120)
  --open                Only show open (or possibly open) ports
  --verbose, -v         Verbose mode

e.g : ./port_scanner.py -target 192.168.1.127,localhost,kali -port 21,22,80,440-500 --open
      ./port_scanner.py -target 192.168.1.0/24,10.0.0.1/24 -port 21,22,80,440-500 --open -v

Role :  Create a script to scan hosts/ a LAN in selecting port or/and range of ports
        I have created a program who create queue and thread to launch tasks
        All params are put in the queue 
        The queue is treated by X instances of threads to accelerate the scan
        Script has been done especially for PWK test to help me to understand how to hack / scan ... servers 
        and perhaps win time for the test. 
    
In Progress : Include banner grabbing

Next Feature :  I am going to include the next actions regarding a specific port 
                do action 
                For instance, an HTTP server, take the banner an provide informations 
                to accelerate the resolution to hack this port on this server
                ( to avoid a HTTP hidden on an exotic port number )

If you would like to use this script, no problem but you have to understand how it work.
It the goal of this script.
