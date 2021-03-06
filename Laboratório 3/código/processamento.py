import socket
import select
import sys
import threading
from dados import openFile

HOST = '' 
PORTA = 5010 # porta que a aplicacao esta usando

# cria um socket para comunicacao
sock = socket.socket() 
# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

#torna o socket não bloqueante
sock.setblocking(False)


inputList = [sys.stdin, sock]



def new_connection(newSock, endereco):
	while True:
		# depois de conectar-se, espera uma mensagem
		msg = newSock.recv(1024) 

		if not msg: break 
		
		try:
			# separa o endereco do arquivo e a palavra a ser buscada
			file_address, word = str(msg, encoding='utf-8').split(";")
			try:
				#abre arquivo
				text = openFile(file_address)
			except Exception as e:
				# envia mensagem de resposta com codigo da excecao
				newSock.send(bytes(str(e), "utf8"))
				continue
				
			# envia mensagem de resposta com o numero de ocorrencias da palavra no texto
			newSock.send(bytes(str(text.split().count(word)), "utf8")) 
		except Exception as e:
			# envia mensagem de resposta com codigo da excecao
			newSock.send(bytes("-2", "utf8"))
			continue
	# fecha o socket da conexao
	newSock.close()


print("Type 'exit' to exit")
while True:
	
	#select em espera para sock ou entrada padrão
	rlist, wlist, xlist = select.select(inputList, [], [])
	
	clientsList = [] #threads ativas
	for newInput in rlist:
		if newInput == sock:
			# aceita a primeira conexao da fila
			newSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
			# aceita nova conexão criando nova thread
			client = threading.Thread(target = new_connection, args=(newSock, endereco))
			client.start()
			clientsList.append(client)

		elif newInput == sys.stdin:
			#le comando digitado pelo usuário na entrada padrão
			cmd = input()
			if(cmd == 'exit'):
				#espera todas as threads ativas terminarem
				for client in clientsList:
					client.join()
				# fecha o socket principal
				sock.close() 
				sys.exit()
			
	

