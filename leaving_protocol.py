import socket, pickle
 
import threading
from threading import Lock
import supernode_variables
import user_variables
import time
try:
    import queue
except ImportError:
    import Queue as queue

def leaving_protocol(port_no):
	try:	
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('',port_no))
		s.listen(102)
		while True:
			conn, addr = s.accept()

			data = conn.recv(4096)
			data_received = pickle.loads(data)
			

			if data_received['msg_type'] == supernode_variables.LEAVE:
				print str(addr[0])+': leaving...'
				print data_received
				supernode_variables.mutex.acquire()
				supernode_variables.index_array[supernode_variables.ip_to_index_map[addr[0]]] = 0
				del supernode_variables.ip_to_index_map[addr[0]]

				for ip,value in supernode_variables.ip_to_index_map:
					msg = {}
					send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					send_socket.connect((ip,user_variables.leaving_port))
					msg = {}
					msg['msg_type'] = supernode_variables.LEAVE
					msg['index'] = data_received['index']
					send_socket.send(pickle.dumps(msg))
					send_socket.close()

				supernode_variables.mutex.release()

			conn.close()
	finally:
		s.close()