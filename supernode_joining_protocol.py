import socket, pickle
import queue 
import threading
from threading import Lock
import supernode_variables
import user_variables
import time
def start_joining_protocol(port_no):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostbyname(socket.gethostname()),port_no))
	s.listen(102)
	while True:	
		conn, addr = s.accept()
		print 'Connected by', addr
		data = conn.recv(4096)
		data_received = pickle.loads(data)
		supernode_variables.mutex.acquire()
		for i in range(100):
			if supernode_variables.index_array[i] == 0:
				supernode_variables.index_array[i] = 1
				return_index = i
				supernode_variables.ip_to_index_map[addr[0]] = i
				break
		msg = {}
		send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'addr[0]:' + addr[0]
		print type(addr[0])
		time.sleep(5)
		send_socket.connect((addr[0],user_variables.joining_port))
		msg['msg_type'] = 'reply_join'
		msg['index'] = return_index
		send_socket.send(pickle.dumps(msg) )
		send_socket.close()
		print 'reply_join sent to user'
		print supernode_variables.ip_to_index_map
		supernode_variables.mutex.release()
		conn.close()
		print data_received
		# Access the information by doing data_variable.process_id or data_variable.task_id etc..,
		print 'Data received from client at addr:' + str(addr[0])