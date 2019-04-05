import socket, pickle
<<<<<<< HEAD 
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
<<<<<<< HEAD
t1 = threading.Thread(target=supernode_joining_protocol.start_joining_protocol, args=(supernode_variables.joining_port,))
t1.start()
=======







HOST = 'localhost'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr

data = conn.recv(4096)
data_variable = pickle.loads(data)
conn.close()
print data_variable
# Access the information by doing data_variable.process_id or data_variable.task_id etc..,
print 'Data received from clien at addr:' + str(addr[0])
>>>>>>> cc2c72ee534b59130d8865f9fe61a14ebe0b4fff
