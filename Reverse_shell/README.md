The goal of these 2 scripts is to create a meterpreter 'like' in python 

The server is listen.
If you launch the client with the parameters of the server, you have some actions to do. 

Server.py
Create a socket in listen mode. Few sessions are allowed.
It is the attacker machine.
A new thread is launched for each session.
