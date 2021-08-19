import socket

HOST = '' 
PORTA = 5505


sock = socket.socket() 
sock.bind((HOST, PORTA))

sock.listen(5) 


novoSock, endereco = sock.accept() 
	
while True:
	msg = novoSock.recv(1024) 

	if not msg: break 
	
	novoSock.send(msg) 
	if(str(msg,  encoding='utf-8') == "break"):
		break


novoSock.close() 

sock.close() 
