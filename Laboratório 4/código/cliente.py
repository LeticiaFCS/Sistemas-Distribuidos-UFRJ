from sys import stdin
from select import select

import socket

# pede para o usuário digitar o endereço do arquivo e palavra
def msg_type():
	print("Type 'list' to list activated users")
	print("Type the user_id';'msg to send msg to user_id")
	print("\tType 'ctrl+d' to exit")

#decodifica a mensagem de retorno
def decode_ret(msg):
	print(msg)
	if(msg[0] == '\x00'):
		id_from, m = msg[1:].split('\x00')
		print("New message:")
		print("\t"+id_from+" : "+m) 
			
	else:
		print("Active users")
		activeUsers = msg.split('\x00')
		for u in activeUsers:
			print(u)




def encode_input(msg):
	if msg.find(";") != -1:
		return msg.replace(";", "\x00", 1)
	elif(msg == "list"):
		return '\x00'
	else:
		raise Exception("wrong input format")
	
	
HOST = 'localhost' # maquina onde esta o servidor
PORTA = 5003 # porta que o servidor esta escutando

# cria socket
sock = socket.socket() 
# conecta-se com o servidor
sock.connect((HOST, PORTA)) 

inputList = [stdin, sock]

msg_type()


while True:
	#select em espera para sock ou entrada padrão
	rlist, wlist, xlist = select(inputList, [], [])
	for newInput in rlist:
		if newInput == sock:
			#espera a resposta do servidor
			returned_msg = sock.recv(1024)			
			decode_ret( str(returned_msg,  encoding='utf-8') )
		elif newInput == stdin:
			line = stdin.readline()
			cmd = line[:-1]
			if(cmd != "exit"):
				try:
					msg = encode_input(cmd)		
					# envia uma mensagem para o servidor
					sock.send(bytes(msg, "utf8"))
					
					
					
					
				except Exception as e:
					print(e)
			else:
				sock.close()
				exit()
		msg_type()	
		


