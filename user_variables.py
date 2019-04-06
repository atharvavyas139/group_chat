import socket, pickle
import queue
import threading
from threading import Lock 


######### Message Type 
JOIN = 1
REPLY_JOIN = 2
HELLO = 3
REPLY_HELLO = 4
LEAVE = 5
TEXT_MSG = 6
ACK = 7
UPDATE = 8 # Crash recovery 


############local variable go here##############################
supernode_ips = ['127.0.0.1'] # need to add elements
timestamp = [0 for x in range(100)]
ip_to_index_map = {}
received_ips = []
self_index = -1 # gets from super node
self_ip = '127.0.0.1'
joining_port = 50111 #fixed for the application
join_complete = False 
# message_queue = for cbcast 