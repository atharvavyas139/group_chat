import socket, pickle
import queue
import user_variables
import supernode_variables
import threading
from threading import Lock 
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
def join():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((user_variables.supernode_ips[0],supernode_variables.joining_port))
    msg = {}
    msg['msg_type'] = 'join'
    msg['ip'] = user_variables.self_ip
    s.send(pickle.dumps(msg) )
    s.close()
    print 'Data Sent to Server'
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'user ---'  + str(user_variables.self_ip)
    receive_socket.bind((user_variables.self_ip,user_variables.joining_port))
    receive_socket.listen(1)
    conn, addr = receive_socket.accept()
    print 'Connected by', addr
    data = conn.recv(4096)
    data_received = pickle.loads(data)
    print 'data_received:'
    print data_received

############## startup goes here ##############
join()
