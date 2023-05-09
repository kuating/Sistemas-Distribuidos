#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading
import json
import os
import re

HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10002 # porta de acesso

entradas = [sys.stdin] #MUDAR
conexoes = {}

dicionario = {}

lock = threading.Lock()

#Dicionario - Carrega dicionario de um json
def carregaDicionario():
	if os.path.exists("dicionario.txt"):
		with open("dicionario.txt", "r") as arquivo:
			global dicionario
			dicionario = json.load(arquivo)

#Dicionario - Salva da variavel dicionario em um json
def salvaDicionario():
	print("Salvando dicionario")
	with open("dicionario.txt", "w") as fp:
		json.dump(dicionario, fp)  # encode dict into JSON
	print("Dicionario salvo")

#Dicionario - print geral para o servidor
def mostraDicionario():
	print(dicionario)

#Dicionario - verificar existencia de chave
def contemDicionario(chave):
	return chave in dicionario

#Dicionario - remove chave
def popDicionario(chave):
	dicionario.pop(chave)

#Dicionario - adiciona na lista e mantem ordem alfabetica
def addSortDicionario(chave,v):
	if(contemDicionario(chave)):
		dicionario[chave].append(v)
		dicionario[chave].sort()
	else:
		dicionario[chave]=[v]
#Dicionario - consulta valor em chave
def getDicionario(chave):
	return dicionario[chave]

def iniciaServidor():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 
	sock.bind((HOST, PORT))
	sock.listen(5) 
	#sock.setblocking(False)
	entradas.append(sock)
	return sock

def aceitaConexao(sock):
	'''Aceita o pedido de conexao de um cliente
	Entrada: o socket do servidor
	Saida: o novo socket da conexao e o endereco do cliente'''
	clisock, endr = sock.accept()
	conexoes[clisock] = endr 
	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''

	while True:
		data = clisock.recv(1024) 
		if not data: # dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			clisock.close() # encerra a conexao com o cliente
			return
		print(str(endr) + ': ')
		entrada = str(data, encoding='utf-8').split('\n')[1:]
		for comando in entrada:
			#match de regex para comandos
			read_match = re.match(r'^read\s+"(.+)"$', comando)
			write_match = re.match(r'^write\s+"(.+)"\s+"(.+)"$', comando)
			
			if read_match:
				chave = read_match.group(1)
				lock.acquire()
				if(contemDicionario(chave)):
					msg = f"D[\'{chave}\']={getDicionario(chave)}"
				else:
					msg = f"D[\'{chave}\']=[]"
				lock.release()
				print(f"checou D[\'{chave}\'].")
				clisock.send(msg.encode('utf-8'))
			
			elif write_match:
				chave = write_match.group(1)
				conteudo = write_match.group(2)
				lock.acquire()
				if(contemDicionario(chave)):
					addSortDicionario(chave,conteudo)
					salvaDicionario()
					print(f"adicionou valor \'{conteudo}\' a D[\'{chave}\']. Chave já existia.")
					msg = f"D[\'{chave}\'] já existia, valor \'{conteudo}\' adicionado"
				else:
					addSortDicionario(chave,conteudo)
					salvaDicionario()
					print(f"adicionou valor \'{conteudo}\' a D[\'{chave}\']. Chave não existia.")
					msg = f"D[\'{chave}\'] não existia, valor \'{conteudo}\' adicionado"
				lock.release()
				clisock.send(msg.encode('utf-8'))
			
			else:
				print(f"enviou comando desconhecido.")
				msg = f"Comando não reconhecido, utilize read \"chave\" ou write \"chave\" \"valor\"."
				clisock.send(msg.encode('utf-8'))

def trataRequisicaoServidor():
	cmd = input()
	remove_match = re.match(r'^remove\s+"(.+)"$', cmd)
	if cmd == 'fim': #solicitacao de finalizacao do servidor
		return True
		
	elif remove_match:
		chave = remove_match.group(1)
		lock.acquire()
		if(contemDicionario(chave)):
			popDicionario(chave)
			salvaDicionario()
			print(f"Chave \'{chave}\' removida.")
		else:
			print(f"Chave \'{chave}\' inexistente.")
		lock.release()
	elif cmd == 'hist': #outro exemplo de comando para o servidor
		print(str(conexoes.values()))
	elif cmd == 'print':
		lock.acquire()
		mostraDicionario()
		lock.release()
	else:
		print("Comando não reconhecido")
	return False

def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	print("\nBem vindo ao dicionário remoto do Rafael!\n")
	print("São quatro comandos disponíveis para o servidor:")
	print("  -remove \"chave\" -> deleta chave do dicionário")
	print("  -fim -> após todos os clientes atuais encerrarem, o servidor encerra também")
	print("  -hist -> conexões atuais")
	print("  -print -> mostra o dicionário todo")
	print("Boa diversão!\n")
	carregaDicionario() #carrega o dicionário salvo
	clientes=[] #armazena as threads criadas para fazer join
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	while True:
		leitura, escrita, excecao = select.select(entradas, [], [])
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = aceitaConexao(sock)
				print ('Conectado com: ', endr)
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr))
				cliente.start()
				clientes.append(cliente) #armazena a referencia da thread para usar com join()
			elif pronto == sys.stdin: #entrada padrao
				fim = trataRequisicaoServidor()
				if(fim):
					for c in clientes: #aguarda todas as threads terminarem
						c.join()
					sock.close()
					salvaDicionario() #Não preciso de join, pois threads morreram e nao aceito mais conexões
					sys.exit()
main()