import socket, pickle
try:
    import queue
except ImportError:
    import Queue as queue
import threading
from threading import Lock
import supernode_variables
import supernode_joining_protocol
import leaving_protocol
import struct
import time
import select

def startup(port_no):
	print("starting supernode")
	for ip in supernode_variables.supernode_ips:
		try:
			if (ip == supernode_variables.self_ip):
				continue
			print("sending update requests to supernode : ",ip,supernode_variables.recovery_port)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip,supernode_variables.recovery_port))
			msg = {}
			msg['msg_type'] = supernode_variables.UPDATE
			s.send(pickle.dumps(msg))
			s.close()
			print("update request sent")
			update_vars(port_no)
			print("updated metadata")
		except Exception,e:
			s.close()
			print("exception in startup : ",e)
			pass



	supernode_variables.mutex.acquire()
	
	while (not supernode_variables.message_wait_queue.empty()):
		queue_element = supernode_variables.message_wait_queue.get()
		addr = queue_element['addr']
		data_received = queue_element['data_received']
		if(data_received['msg_type'] == supernode_variables.JOIN):
			supernode_joining_protocol.join_util(addr,data_received)
		else:
			leaving_protocol.leave_util(addr,data_received)
	supernode_variables.update_complete = True

	supernode_variables.mutex.release()

	update_reply(port_no)

def update_vars(port_no):
	print("udpating vars")
	try:
		
		receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		receive_socket.bind(('', port_no))
		
		receive_socket.setblocking(1)              #go back to blocking mode
		# receive_socket.setblocking(0)
		print("setting timeout")
		# timeout set to 1 sec
		tv = struct.pack("ll", 1, 0)
		receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, tv)
		receive_socket.listen(1)

		# receive_socket.settimeout(1.0)
		# receive_socket.listen(1)

		print("accepting connection")
		conn, addr = receive_socket.accept()
		print("accepted connection")
		data = conn.recv(4096)
		


		print("received metadata from supernode : ",addr)
		data_received = pickle.loads(data)
		supernode_variables.mutex.acquire()

		supernode_variables.index_array = data_received['index_array']
		supernode_variables.ip_to_username = data_received['ip_to_username']
		supernode_variables.ip_to_index_map = data_received['ip_to_index_map']
	except Exception,e:
		print("problem in update_vars :",e)
	finally:
		conn.close()
		receive_socket.close()
		supernode_variables.mutex.release()

def update_reply(port_no):
	print("listening for update requests")
	try:
		while True:
			receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			receive_socket.bind(('',port_no))
			receive_socket.listen(102)

			conn, addr = receive_socket.accept()
			data = conn.recv(4096)
			conn.close()
			receive_socket.close()
			msg = pickle.loads(data)

			print("sending metadata to : ",addr)
			if (msg['msg_type'] == supernode_variables.UPDATE):
				supernode_variables.mutex.acquire()
				data_send = {}
				data_send['index_array'] = supernode_variables.index_array
				data_send['ip_to_username'] = supernode_variables.ip_to_username
				data_send['ip_to_index_map'] = supernode_variables.ip_to_index_map
				supernode_variables.mutex.release()
				try:
					send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					send_socket.connect((addr[0],port_no))
					send_socket.send(pickle.dumps(data_send) )
					send_socket.close()
				except:
					print("problem in sending metadata")
					send_socket.close()
	except Exception,e:
		print("problem in update_reply : ",e)
		receive_socket.close()