from sys import stdin

import socket

# pede para o usuário digitar o endereço do arquivo e palavra
def msg_type():
	print("Type the file address and the word to be searched split by ';'")
	print("\tType 'ctrl+d' to exit")
	print("\tE.g.: test.txt;pedra")

#decodifica a mensagem de retorno
def decode_ret(msg):
	print("---")
	if(msg == "-1"):
		print("File not found!")
	elif(msg == "-2"):
		print("Wrong input format!")
	else:
		print("There are "+msg+" occurrences of the word in the file")
	print("---")

HOST = 'localhost' # maquina onde esta o servidor
PORTA = 5007 # porta que o servidor esta escutando

# cria socket
sock = socket.socket() 
# conecta-se com o servidor
sock.connect((HOST, PORTA)) 

msg_type()

#para cada linha digitada
for line in stdin:
	#descarta '\n'
	msg = line[:-1]
	# envia uma mensagem para o servidor
	sock.send(bytes(msg, "utf8"))
	
	#espera a resposta do servidor
	returned_msg = sock.recv(1024)
	
	decode_ret( str(returned_msg,  encoding='utf-8') )
	
	msg_type()
	
# encerra a conexao
sock.close() 
