import socket
from dados import openFile

HOST = '' 
PORTA = 5007 # porta que a aplicacao esta usando

# cria um socket para comunicacao
sock = socket.socket() 
# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

# define o limite maximo de espera por conexao
sock.settimeout(20)

while True:
	# aceita a primeira conexao da fila
	newSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
		
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
	
# fecha o socket principal
sock.close() 
