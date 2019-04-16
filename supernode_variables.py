import socket, pickle
try:
    import queue
except ImportError:
    import Queue as queue
import threading
from threading import Lock
#####################mutex wale ######################
mutex = Lock()
index_array = [0 for x in range(100)]
ip_to_username = {}
ip_to_index_map = {}


######### Message Type 
JOIN = 1
REPLY_JOIN = 2
HELLO = 3
REPLY_HELLO = 4
LEAVE = 5
TEXT_MSG = 6
ACK = 7
UPDATE = 8 # Crash recovery 




####################fixed wale####################
supernode_ips = [] 
message_wait_queue = queue.Queue()
self_ip = '10.117.2.134'
joining_port = 50019
leaving_port = 50021
