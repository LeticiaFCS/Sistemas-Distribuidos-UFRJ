import socket
import select
import sys
import threading
from queue import Queue

HOST = '' 
PORTA = 5003 # porta que a aplicacao esta usando

# cria um socket para comunicacao
sock = socket.socket() 
# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

#torna o socket não bloqueante
sock.setblocking(False)


inputList = [sys.stdin, sock]

clientsActive = {} #threads ativas
ids = [] #ids de cada cliente
sockets = [] #socket de cada cliente

msgQueue = Queue(maxsize = 1000)

#classe que reprensenta o tipo mensagem
class Msg():
	def __init__(self, id_from, id_to, m, block = False, timeout = None):
		self.id_from = id_from
		self.id_to = id_to
		self.m = m


#classe responsável por fazer as operações na fila de forma bloqueante
class ReadMsg():		
	def __init__(self, block = False, timeout = None):
		self.block = block
		self.timeout = timeout
	
	def __enter__(self):
		try:
			return msgQueue.get(self.block, self.timeout)
		except:
			return None
	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass
	


def new_connection(newSock, id):
	while True:
		# depois de conectar-se, espera uma mensagem
		msg = newSock.recv(1024) 
		# se o cliente desconectou
		if not msg: break 
		
		# listar clientes 
		if( str(msg,  encoding='utf-8') == '\x00'):
			act = ""
			for thr, a in clientsActive.items():
				if(a):
					act = act + str(thr) + '\x00'
			if(act == ""):
				act = "Nenhum usuário ativo"+ '\x00'
			newSock.send(bytes(act, "utf8")) 
		elif( str(msg,  encoding='utf-8') == '\x01'):
			if(clientsActive[id]):
				msgQueue.put(Msg(-1, id, "O seu estado eh verdadeiro"))
			else:
				msgQueue.put(Msg(-1, id, "O seu estado eh falso"))
				
		elif( str(msg,  encoding='utf-8') == '\x02'):
			clientsActive[id] = not clientsActive[id]
			msgQueue.put(Msg(-1, id, "Seu estado foi mudado!"))
		elif( str(msg,  encoding='utf-8') == '\x03'):
			msgQueue.put(Msg(-1, id, "Seu id eh "+str(id)))
		else:
			msgList = str(msg,  encoding='utf-8').split('\x00')
			if(len(msgList) != 2):
				continue
			idTo, m = msgList
			newMsg = Msg(id, int(idTo), m)
			if(clientsActive[id] and clientsActive[int(idTo)]):
				msgQueue.put(newMsg)
			elif(not clientsActive[id] and not clientsActive[int(idTo)]):
				msgQueue.put(Msg(-1, id, "A mensagem '"+m+"' para "+idTo+" nao foi enviada porque remetente e destinatario estao inativos"))
			elif(not clientsActive[id]):
				msgQueue.put(Msg(-1, id, "A mensagem '"+m+"' para "+idTo+" nao foi enviada porque remetente esta inativo"))			
			else:
				msgQueue.put(Msg(-1, id, "A mensagem '"+m+"' para "+idTo+" nao foi enviada porque destinatario esta inativo"))		
		
		
		
		
		
	# fecha o socket da conexao
	newSock.close()
	clientsActive[id] = False


	
#Método pega próxima mensagem da fila de forma bloqueante
def nxtMsg(block = True, timeout = 30):
	while not msgQueue.empty():
		with ReadMsg(block, timeout) as msg:
			yield msg

exited = False
#Método da thread que envia as mensagens na ordem que foram enfileiradas
def send_msgs():
	while not exited:
		for msg in nxtMsg():
			if(msg == None):
				if(exited):
					break
				else:
					continue			
			m = '\x00' + str(msg.id_from) + '\x00' + str(msg.m)
			sockets[msg.id_to].send( bytes(m, "utf8") )
				

			
		
		
print("Digite 'sair' para sair")
while True:
	
	#select em espera para sock ou entrada padrão
	rlist, wlist, xlist = select.select(inputList, [], [])
	
	sender = threading.Thread(target = send_msgs, args=())
	sender.start()

	for newInput in rlist:
		if newInput == sock:
			# aceita a primeira conexao da fila
			newSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
			# aceita nova conexão criando nova thread
			client = threading.Thread(target = new_connection, args=(newSock, len(ids)))
			
			ids.append(client)
			sockets.append(newSock)
			clientsActive[len(ids) - 1] = True
			client.start()
			
		elif newInput == sys.stdin:
			#le comando digitado pelo usuário na entrada padrão
			cmd = input()
			if(cmd == 'sair'):
				#espera todas as threads ativas terminarem
				for client in ids:
					client.join()
				exited = True
				sender.join()
				# fecha o socket principal
				sock.close() 
				sys.exit()
			
	

