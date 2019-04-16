import socket, pickle
import Queue as queue
import threading
from threading import Lock 
import os
from subprocess import Popen, PIPE
import time


######### Message Type 
JOIN = 1
REPLY_JOIN = 2
HELLO = 3
REPLY_HELLO = 4
LEAVE = 5
TEXT_MSG = 6
ACK = 7
UPDATE = 8 # Crash recovery 



#####################mutex wale ######################
mutex = Lock()
timestamp = [0 for x in range(100)]
ip_to_index_map = {}

############local variable go here##############################
supernode_ips =  ['10.117.12.118'] # need to add elements
supernode_ports = [50019]	# will be fixed for all supernodes 
received_ips = []
self_index = -1 # gets from super node
self_ip = '10.117.12.118'
joining_port = 50111 #fixed for the application across all the users 
sending_port = 50112
receiving_port = 50113
supernode_leaving_port = 50021
leaving_port = 50114
join_complete = False
priority_queue= queue.PriorityQueue() 
# message_queue = for cbcast

########################priority queue #######################
class QueueElement(object): 
	def __init__(self, time_stamp, time_received, message, index): 
		self.timestamp = time_stamp
		self.time_received = time_received
		self.message = message
		self.index = index
	def __str__(self):
		return "({0})".format(self.message)

	def __lt__(self, other):
		b = True
		for i in range(100):
			if self.timestamp[i] <= other.timestamp[i]:
				b = b and True
			else:
				b = b and False
		if b: # defintely less than
			return True
		
		b = True
		for i in range(100):
			if self.timestamp[i] >= other.timestamp[i]:
				b = b and True
			else:
				b = b and False
		if b: # definitely greater 
			return False
		#if concurrent
		return self.time_received < other.time_received
"""an example of usage
timestamp1 = [0 for x in range(100)]
timestamp1[1] = 1
timestamp1[3] = 4
rt1 = time.time()
msg1 = "message1"
priority_queue.put(QueueElement(timestamp1, rt1, msg1, index))
while not priority_queue.empty():
	myt = priority_queue.get()
	print 'Processing level:', myt
"""

