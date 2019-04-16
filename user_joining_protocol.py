import socket, pickle
import user_variables
import sys
import supernode_variables
import threading
from threading import Lock 
import struct
import Queue as queue
import time
import xterm
############ structure of msg goes here should not exceed 4kB ###
"""
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip'] = ""
msg['username'] = ""
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
            # print 'Connected by', addr
            data = conn.recv(4096)
            data_received = pickle.loads(data)
            if data_received['msg_type'] == user_variables.HELLO:
                ##
                user_variables.mutex.acquire()
                user_variables.ip_to_index_map[addr[0]] = data_received['index']
                user_variables.ip_to_username[addr[0]] = data_received['username']
                xterm.print_xterm_message(data_received['username'] + ' joined the chat')
                user_variables.mutex.release()

                ## send back the reply 
                msg = {}
                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print 'reply being sent to addr[0]:' + addr[0]
                # print type(addr[0])
                send_socket.connect((addr[0],user_variables.joining_port))
                msg['msg_type'] = user_variables.REPLY_HELLO
                msg['index'] = user_variables.self_index
                msg['timestamp'] = user_variables.timestamp
                # print 'message sent'
                send_socket.send(pickle.dumps(msg) )
                send_socket.close()
    finally:
        s.close()



## to send msgs to all the users in the group 
def send_to_all(msg):

    # set the send recieve port based on the msg_type
    if(msg['msg_type'] == user_variables.HELLO):
        send_port = user_variables.joining_port
        receive_port = user_variables.joining_port
    else:
        if(msg['msg_type'] == user_variables.TEXT_MSG):
            # msg will be send to the receiving_port of the receiver 
            send_port = user_variables.receiving_port
            receive_port = user_variables.sending_port


    for ip in user_variables.ip_to_index_map:
        if(ip != user_variables.self_ip):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((ip,send_port))
                # print 'msg type ' +str(msg['msg_type']) + ' sent to '+ str(ip) 
                s.send(pickle.dumps(msg) )
                s.close()
                # wait for message receive 
                receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                receive_socket.bind(('', receive_port))
                receive_socket.setblocking(1)              #go back to blocking mode

                ## timeout set to 1 sec
                tv = struct.pack("ll", 1, 0)
                receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, tv)
                receive_socket.listen(1)

                conn, addr = receive_socket.accept()
                # print 'Connected Successfully by', addr
                data = conn.recv(4096)
                data_received = pickle.loads(data)
                receive_socket.close()

                ## update the local timestamp with the timestamp received if the msg_type is HELLO 
                if(msg['msg_type'] == user_variables.HELLO):
                    user_variables.mutex.acquire()
                    for i in range(100):
                        user_variables.timestamp[i] = max(user_variables.timestamp[i], data_received['timestamp'][i])
                    user_variables.mutex.release()

            except :
                # print str(ip) + ' time out '
                logout(ip)
                # CALL LEAVING PROTOCOL send leave message to supernode on the leave port 
            finally:
                s.close()
                receive_socket.close()

#### updates the vector clock when a message is delivered
def update_vector_clock(timestamp):
    user_variables.mutex.acquire()

    for i in range(100):
        user_variables.timestamp[i] = max(user_variables.timestamp[i], timestamp[i])

    user_variables.mutex.release()


## receive check 
def receive_msg():
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.bind((supernode_variables.self_ip,port_no))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',user_variables.receiving_port))
        s.listen(102)
        while True:
            conn, addr = s.accept()
            # print 'Connected by', addr
            data = conn.recv(4096)
            data_received = pickle.loads(data)
            time_received = time.time()            
            # print str(addr[0])+':' + data_received['text_msg']
            ## send back the reply 
            msg = {}
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # print 'reply being sent to addr[0]:' + addr[0]
            send_socket.connect((addr[0],user_variables.sending_port))
            msg['msg_type'] = user_variables.ACK
            msg['index'] = user_variables.self_index
            msg['timestamp'] = user_variables.timestamp
            # print 'ACK message sent'
            send_socket.send(pickle.dumps(msg) )
            send_socket.close()
            user_variables.priority_queue.put(user_variables.QueueElement(data_received['timestamp'], 
            time_received, data_received['username'] +': ' +data_received['text_msg'], data_received['index']))
            while True:
                if user_variables.priority_queue.empty():
                    break
                queue_element = user_variables.priority_queue.get()
                first_index = queue_element.index
                i = -1
                for i in range(101):
                    if i == 100:
                        break
                    if i == first_index:
                        if user_variables.timestamp[i] != queue_element.timestamp[i] -1:
                            break
                    else:
                        if user_variables.timestamp[i] < queue_element.timestamp[i]:
                            break
                # print 'i break at:' + str(i)
                if i == 100: #condition to deliver message is true
                    update_vector_clock(queue_element.timestamp)
                    # print 'send to xterm:' + str(queue_element.message)
                    xterm.print_xterm_message(queue_element.message)
                else:# put back the element again
                    user_variables.priority_queue.put(queue_element)
                    break

    finally:
        s.close()


# fiunction to send the message to the other users 
def send_txt_msg():
    while(True):
        message = raw_input(str(user_variables.username)+'$ ')
        if(message == 'logout'):
            print 'logout done '
            logout('0')
        else:
            xterm.print_xterm_message(user_variables.username +': ' +message)
            msg = {}
            msg['msg_type'] = user_variables.TEXT_MSG
            msg['index'] = user_variables.self_index
            msg['text_msg'] = message
            msg['timestamp'] = user_variables.timestamp
            msg['username'] = user_variables.username
            user_variables.timestamp[user_variables.self_index] += 1
            send_to_all(msg)


## send hello to all the other nodes 
def hello_users():
    msg = {}
    msg['msg_type'] = user_variables.HELLO
    msg['index'] = user_variables.self_index
    msg['username'] = user_variables.username
    send_to_all(msg)

    ## joining protocol complete now  
    user_variables.join_complete = True
    # print 'join complete'
    t1 = threading.Thread(target=send_reply_hello, args=())
    t1.start()
    # t4 = threading.Thread(target=logout, args=())
    # t4.start()
    t2 = threading.Thread(target=send_txt_msg, args=())
    t2.start()
    t3 = threading.Thread(target=receive_msg, args=())
    t3.start()
    t4 = threading.Thread(target=leave_update, args= ())
    t4.start()



### reply_join function
def reply_join():
    try:
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        receive_socket.bind(('',user_variables.joining_port))
        receive_socket.listen(1)
        conn, addr = receive_socket.accept()
        # print 'Connected by', addr
        data = conn.recv(4096)
        data_received = pickle.loads(data)
        receive_socket.close()

        user_variables.mutex.acquire()
        user_variables.ip_to_index_map = data_received['ip_to_index']
        user_variables.self_index = data_received['index']
        user_variables.ip_to_username = data_received['ip_to_username']
        user_variables.mutex.release()

        # print 'index received '+ str(user_variables.self_index)
        ## send hello msg to all the other users in the chat 
        hello_users()

    finally:
        receive_socket.close()


## join start 
def start_join():
    user_variables.username = raw_input('Enter a user name : ')
    time.sleep(1.0)
    xterm.print_xterm_message('Welcome '+user_variables.username)
    for i in range(1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((user_variables.supernode_ips[i],user_variables.supernode_ports[0]))
        msg = {}
        msg['msg_type'] = user_variables.JOIN
        msg['ip'] = user_variables.self_ip
        msg['username'] = user_variables.username
        s.send(pickle.dumps(msg) )
        s.close()
        # print 'Data Sent to Server'
        print 'user ---'  + str(user_variables.self_ip)

        #### waiting for reply join 
        reply_join()

############## startup goes here ##############





######### Leave functions ######
def leave_update():
        
            receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            receive_socket.bind(('',user_variables.leaving_port))
            receive_socket.listen(102)
            try:
                while True: 
                    conn, addr = receive_socket.accept()
                    data = conn.recv(4096)
                    data_received = pickle.loads(data)
                    if data_received['ip'] in user_variables.ip_to_index_map.keys():
                        xterm.print_xterm_message(user_variables.ip_to_username[data_received['ip']] + ' left the chat')
                        # print str(data_received['ip'])+': leaving...'


                        ## update the timestamp and ip_to_index_map 
                        user_variables.mutex.acquire()
                        user_variables.timestamp[user_variables.ip_to_index_map[data_received['ip']]] = 0
                        del user_variables.ip_to_index_map[data_received['ip']]
                        del user_variables.ip_to_username[data_received['ip']]
                        user_variables.mutex.release()
            finally:
                receive_socket.close()



def logout(ip):
    # while True:
    msg = {}
    msg['msg_type'] = user_variables.LEAVE
    msg['ip'] = ip
    if ip == '0':
        msg['ip'] = user_variables.self_ip
    for i in range(1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((user_variables.supernode_ips[i],user_variables.supernode_leaving_port))
        s.send(pickle.dumps(msg) )
        s.close()
        
    print ('Leave message sent to the Server')
    if ip == '0':
        sys.exit(0)