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
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('',port_no))
		s.listen(102)
		while True:
			try:
				conn, addr = s.accept()

				data = conn.recv(4096)
				data_received = pickle.loads(data)
				
				if (data_received['ip'] not in supernode_variables.ip_to_index_map):
					conn.close()
					continue

				supernode_variables.mutex.acquire()
				if(supernode_variables.update_complete == False):
					queue_element = {}
					queue_element['addr'] = addr
					queue_element['data_received'] = data_received
					supernode_variables.message_wait_queue.put(queue_element)
				else:
					leave_util(addr,data_received)

			except Exception,e:
				print("problem encountered in leaving user : ",e)
			finally:
				supernode_variables.mutex.release()
				conn.close()
	finally:
		s.close()

def leave_util(addr,data_received):
	## deleting the ip received in the message 
	if data_received['msg_type'] == supernode_variables.LEAVE:
		print str(data_received['ip'])+': '+  str(supernode_variables.ip_to_username[data_received['ip']]) + ' leaving...'
		# print data_received
		supernode_variables.index_array[supernode_variables.ip_to_index_map[data_received['ip']]] = 0
		send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		del supernode_variables.ip_to_index_map[data_received['ip']]
		del supernode_variables.ip_to_username[data_received['ip']]
		for ip in supernode_variables.ip_to_index_map:
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				msg = {}
				send_socket.connect((ip,user_variables.leaving_port))
				msg = {}
				msg['msg_type'] = supernode_variables.LEAVE
				msg['ip'] = data_received['ip']
				send_socket.send(pickle.dumps(msg))

			except Exception,e:
				print("problem encountered in sending leave to : ",ip, ", Exception : ",e)
			finally:
				send_socket.close()
