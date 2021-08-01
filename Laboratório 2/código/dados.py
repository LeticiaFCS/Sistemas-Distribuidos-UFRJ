def openFile(endereco):
	try:
		#abre arquivo
		f = open(endereco, "r")
		# guarda conteudo do arquivo
		text = f.read()
		#fecha arquivo
		f.close()
		# retorna conteudo do arquivo
		return text
	except OSError:
		#codigo da excecao caso nao consiga abrir arquivo
		raise Exception("-1")

