import socket, pickle
import queue 
############structure of msg goes here should not exceed 4kB###
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip'] = ""


############local variable go here##############################
supernode_ips = ['localhost'] # need to add elements
timestamp = [0 for x in range(100)]
ip_to_index_map = {}
received_ips = []
self_index = -1 # gets from super node
self_ip = socket.gethostbyname(socket.gethostname())
port = 50007 #fixed for the application
# message_queue = for cbcast 

#######functions and message handlers go here###

### mutex locks may also be needed to added
def join():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((supernode_ips[0],port))
    msg['msg_type'] = 'join'
    msg['ip'] = self_ip
    s.send(pickle.dumps(msg) )
    s.close()
    print 'Data Sent to Server'


############## startup goes here ##############
join()