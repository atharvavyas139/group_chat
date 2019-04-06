import socket, pickle
import user_variables
import supernode_variables
import user_joining_protocol
import threading
from threading import Lock 
import Queue as queue
############structure of msg goes here should not exceed 4kB###
"""
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip'] = ""
"""

#######functions and message handlers go here###

### mutex locks may also be needed to added


############## startup goes here ##############
t1 = threading.Thread(target=user_joining_protocol.start_join, args=())
t1.start()

# t1 = threading.Thread(target=user_joining_protocol.send_reply_hello, args=())
# t1.start()

