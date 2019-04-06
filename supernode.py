import socket, pickle
import threading
from threading import Lock
import supernode_variables
import supernode_joining_protocol
import Queue as queue
############structure of msg goes here only for variable message field convention #################
# not to be used directly #
"""
############structure of msg goes here #################
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip_address'] = ""
"""
#######functions and signal handlers go here###
t1 = threading.Thread(target=supernode_joining_protocol.start_joining_protocol, args=(supernode_variables.joining_port,))
t1.start()
