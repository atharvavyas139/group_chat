import socket, pickle
import queue 
import threading
from threading import Lock
#####################mutex wale ######################
mutex = Lock()
index_array = [0 for x in range(100)]
ip_to_index_map = {}


####################fixed wale####################
supernode_ips = [] 
message_wait_queue = queue.Queue()
self_ip = '127.0.0.1'
joining_port = 50019