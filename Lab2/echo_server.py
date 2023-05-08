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
PORT = 10001 # porta de acesso

entradas = [socket.socket()] #MUDAR
conexoes = {}

dicionario = {}

def carregaDicionario():
	if os.path.exists("dicionario.txt"):
		with open("dicionario.txt", "r") as arquivo:
			dicionario = json.load(arquivo)

def salvaDicionario():
	print("Salvando dicionario")
	with open("dicionario.txt", "w") as fp:
		json.dump(dicionario, fp)  # encode dict into JSON
	print("Dicionario salvo")

def mostraDicionario():
	print(dicionario)

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
		entrada = str(data, encoding='utf-8').split('\n')
		for comando in entrada:
			#command_string = 'read "filename.txt"'
			# or command_string = 'write "new_file.txt" "Hello, world!"'

			read_match = re.match(r'^read\s+"(.+)"$', comando)
			if read_match:
				chave = read_match.group(1)
				if(chave in dicionario):
					msg = f"D[\'{chave}\']={dicionario[chave]}"
				else:
					msg = f"D[\'{chave}\']=[]"
				print(f"checou D[\'{chave}\']")
				clisock.send(msg.encode('utf-8'))

			# match the write command
			write_match = re.match(r'^write\s+"(.+)"\s+"(.+)"$', comando)
			if write_match:
				chave = write_match.group(1)
				conteudo = write_match.group(2)
				if(chave in dicionario):
					dicionario[chave].append(conteudo)
					dicionario[chave].sort()
					print(f"Chave \'{chave}\' já existia, o valor \'{conteudo}\' foi adicionado.")
					msg = f"D[\'{chave}\']=BLAH"
					clisock.send(msg.encode('utf-8'))
				else:
					dicionario[chave]=[conteudo]
					print(f"Chave \'{chave}\' não existia, o valor \'{conteudo}\' foi adicionado.")
					msg = f"D[\'{chave}\']=BLAH"
					clisock.send(msg.encode('utf-8'))

def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	carregaDicionario()
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
				cmd = input()
				if cmd == 'fim': #solicitacao de finalizacao do servidor
					for c in clientes: #aguarda todas as threads terminarem
						c.join()
					sock.close()
					salvaDicionario()
					sys.exit()
				elif cmd == 'hist': #outro exemplo de comando para o servidor
					print(str(conexoes.values()))
				elif cmd == 'print':
					mostraDicionario()

main()