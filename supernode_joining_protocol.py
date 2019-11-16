import socket, pickle
import Queue as queue
import threading
import time
from threading import Lock
import supernode_variables
import user_variables
import time
def start_joining_protocol(port_no):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# s.bind((supernode_variables.self_ip,port_no))
		s.bind(('',port_no))
		s.listen(102)
		while True:
			try:
				conn, addr = s.accept()
				print 'Connected by', addr
				data = conn.recv(4096)
				data_received = pickle.loads(data)

				supernode_variables.mutex.acquire()
				if(supernode_variables.update_complete == False):
					queue_element = {}
					queue_element['addr'] = addr
					queue_element['data_received'] = data_received
					supernode_variables.message_wait_queue.put(queue_element)
					print("storing request in queue")
				else:
					join_util(addr,data_received)
				
				print data_received
				# Access the information by doing data_variable.process_id or data_variable.task_id etc..,
				print 'Data received from client at addr:' + str(addr[0])
			except Exception,e:
				print("problem in joining a user : ",e)
			finally:
				conn.close()
				supernode_variables.mutex.release()

	except Exception,e:
		print("problem encounter in start_joining_protocol : ",e)
	finally:
		s.close()

def join_util(addr,data_received):
	try:
		supernode_variables.ip_to_username[addr[0]] = data_received['username']
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
		time.sleep(1)
		send_socket.connect((addr[0],user_variables.joining_port))
		msg['msg_type'] = supernode_variables.REPLY_JOIN
		msg['index'] = return_index
		msg['ip_to_index'] = supernode_variables.ip_to_index_map
		msg['ip_to_username'] = supernode_variables.ip_to_username
		send_socket.send(pickle.dumps(msg) )
		print 'reply_join sent to user'
		# print supernode_variables.ip_to_username
	except Exception,e:
		print("Exception encountered in join_util : ",e)
	finally:
		send_socket.close()