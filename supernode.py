import socket, pickle
import Queue as queue
############structure of msg goes here #################
msg = {}
msg['msg_type'] =""
msg['text_msg'] = ""
msg['timestamp'] = [0 for x in range(100)]
msg['ip_to_index'] = {}
msg['index'] = -1
msg['ip_address'] = ""

############local variables go here#################
index_array = [0 for x in range(100)]
ip_to_index_map = {}
supernode_ips = []
message_wait_queue = queue.Queue()

#######functions and signal handlers go here###







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