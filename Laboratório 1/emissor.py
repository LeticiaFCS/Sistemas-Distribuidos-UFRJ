import socket

HOST = 'localhost' 
PORTA = 5505 


sock = socket.socket() 

sock.connect((HOST, PORTA)) 


while True:
	msg = input()
	sock.send(bytes(msg, "utf8"))
	returned_msg = sock.recv(1024)

	print(str(returned_msg,  encoding='utf-8'))
	
	if( str(returned_msg,  encoding='utf-8') == "break" ):
		break

sock.close() 
