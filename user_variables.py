import socket, pickle
import queue
import threading
from threading import Lock 
############local variable go here##############################
supernode_ips = [socket.gethostbyname(socket.gethostname())] # need to add elements
timestamp = [0 for x in range(100)]
ip_to_index_map = {}
received_ips = []
self_index = -1 # gets from super node
self_ip = socket.gethostbyname(socket.gethostname())
joining_port = 50111 #fixed for the application
join_complete = False 
# message_queue = for cbcast 