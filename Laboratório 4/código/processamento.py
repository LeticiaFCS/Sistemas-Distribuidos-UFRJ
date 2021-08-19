import socket
import select
import sys
import threading
from dados import openFile
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
ids = []
sockets = []

msgQueue = Queue(maxsize = 10) #aumentar


class Msg():
	def __init__(self, id_from, id_to, m, block = False, timeout = None):
		self.id_from = id_from
		self.id_to = id_to
		self.m = m

class ReadMsg():		
	def __init__(self, block = False, timeout = None):
		self.block = block
		self.timeout = timeout
	
	def __enter__(self):
		return msgQueue.get(self.block, self.timeout)
	
	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass
	


def new_connection(newSock, id):
	while True:
		# depois de conectar-se, espera uma mensagem
		msg = newSock.recv(1024) 
		if( str(msg,  encoding='utf-8') == '\x00'):
			act = ""
			for thr, a in clientsActive.items():
				if(a):
					act = act + str(thr) + '\x00'
			newSock.send(bytes(act, "utf8"))
		else:
			idTo, m = str(msg,  encoding='utf-8').split('\x00')
			newMsg = Msg(id, int(idTo), m)
			msgQueue.put(newMsg)
		
		if not msg: break 
		
		
		
	# fecha o socket da conexao
	newSock.close()
	clientsActive[id] = False
	

def nxtMsg(block = False, timeout = None):
	while not msgQueue.empty():
		with ReadMsg(block, timeout) as msg:
			yield msg

exited = False
def send_msgs():
	while not exited:
		for msg in nxtMsg():
			m = '\x00' + str(msg.id_from) + '\x00' + str(msg.m)
			sockets[msg.id_to].send( bytes(m, "utf8") )
			
			
		
		
print("Type 'exit' to exit")
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
			client.start()
			ids.append(client)
			sockets.append(newSock)
			clientsActive[len(ids) - 1] = True
			
		elif newInput == sys.stdin:
			#le comando digitado pelo usuário na entrada padrão
			cmd = input()
			if(cmd == 'exit'):
				#espera todas as threads ativas terminarem
				for client in ids:
					client.join()
				exited = True
				sender.join()
				# fecha o socket principal
				sock.close() 
				sys.exit()
			
	

