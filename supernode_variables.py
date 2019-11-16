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
message_wait_queue = queue.Queue()


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
supernode_ips = ['10.5.18.103','10.5.18.104','10.5.18.109']  ## fill the supernode ips accordingly
self_ip = '10.5.18.103'
joining_port = 50019
leaving_port = 50021
update_complete = False
recovery_port = 50100
