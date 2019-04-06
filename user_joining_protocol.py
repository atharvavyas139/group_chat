import socket, pickle
import user_variables
import supernode_variables
import threading
from threading import Lock 
import struct
import Queue as queue
############ structure of msg goes here should not exceed 4kB ###
"""
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip'] = ""
"""

# supernode_ips = ['127.0.0.1'] # need to add elements
# timestamp = [0 for x in range(100)]
# ip_to_index_map = {}
# received_ips = []
# self_index = -1 # gets from super node
# self_ip = '127.0.0.1'
# joining_port = 50111 #fixed for the application
# join_complete = False 

#######functions and message handlers go here###

### mutex locks may also be needed to added



## reply to the hello msgs runs in a new separate thread 

def send_reply_hello():
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.bind((supernode_variables.self_ip,port_no))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',user_variables.joining_port))
        s.listen(102)
        while True:
            conn, addr = s.accept()
            print 'Connected by', addr
            data = conn.recv(4096)
            data_received = pickle.loads(data)

            ##### potentiol deadlock #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            user_variables.mutex.acquire()
            user_variables.ip_to_index_map[addr[0]] = data_received['index']
            user_variables.mutex.release()

            ## send back the reply 
            msg = {}
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print 'reply being sent to addr[0]:' + addr[0]
            print type(addr[0])
            send_socket.connect((addr[0],user_variables.joining_port))
            msg['msg_type'] = user_variables.REPLY_HELLO
            msg['index'] = user_variables.self_index
            msg['timestamp'] = user_variables.timestamp
            print 'message sent'
            send_socket.send(pickle.dumps(msg) )
            send_socket.close()
    finally:
        s.close()

## send hello to all the other nodes 
def hello_users():
    for ip in user_variables.ip_to_index_map:
        if(ip != user_variables.self_ip):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip,user_variables.joining_port))
            msg = {}
            msg['msg_type'] = user_variables.HELLO
            msg['index'] = user_variables.self_index
            try:
                print 'hello msg sent to '+ str(ip) 
                s.send(pickle.dumps(msg) )
                s.close()
                # wait for message receive 
                receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                receive_socket.bind(('',user_variables.joining_port))
                receive_socket.setblocking(1)              #go back to blocking mode

                ## timeout set to 1 sec
                tv = struct.pack("ll", 1, 0)
                receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, tv)
                receive_socket.listen(1)

                conn, addr = receive_socket.accept()
                print 'Connected Successfully by', addr
                data = conn.recv(4096)
                data_received = pickle.loads(data)
                receive_socket.close()

                ## update the local timestamp with the timestamp received 
                user_variables.mutex.acquire()
                for i in range(100):
                    user_variables.timestamp[i] = max(user_variables.timestamp[i], data_received['timestamp'][i])
                user_variables.mutex.release()

            except socket.timeout:
                print str(ip) + ' time out '
                # CALL LEAVING PROTOCOL
            finally:
                receive_socket.close()

    ## joining protocol complete now  
    user_variables.join_complete = True
    print 'join complete'
    t1 = threading.Thread(target=send_reply_hello, args=())
    t1.start()
    t1.join()



### reply_join function
def reply_join():
    try:
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        receive_socket.bind((user_variables.self_ip,user_variables.joining_port))
        receive_socket.listen(1)
        conn, addr = receive_socket.accept()
        print 'Connected by', addr
        data = conn.recv(4096)
        data_received = pickle.loads(data)
        receive_socket.close()

        user_variables.mutex.acquire()
        user_variables.ip_to_index_map = data_received['ip_to_index']
        user_variables.self_index = data_received['index']
        user_variables.mutex.release()

        print 'index received '+ str(user_variables.self_index)
        ## send hello msg to all the other users in the chat 
        hello_users()

    finally:
        receive_socket.close()

def start_join():
    for i in range(1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((user_variables.supernode_ips[i],user_variables.supernode_ports[0]))
        msg = {}
        msg['msg_type'] = user_variables.JOIN
        msg['ip'] = user_variables.self_ip
        s.send(pickle.dumps(msg) )
        s.close()
        print 'Data Sent to Server'
        print 'user ---'  + str(user_variables.self_ip)

        #### waiting for reply join 
        reply_join()

############## startup goes here ##############
