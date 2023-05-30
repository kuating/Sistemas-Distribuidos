# Servidor do Dicionario Remoto
import os
import json
import threading
import rpyc
from rpyc.utils.server import ThreadedServer

lock = threading.Lock()


class Dicionario:
    def __init__(self):
        self.dic = {}

    # Carrega dicionario de um json
    def carrega(self):
        if os.path.exists("dicionario.txt"):
            with open("dicionario.txt", "r") as arquivo:
                self.dic = json.load(arquivo)

    # Salva da variavel dicionario em um json
    def salva(self):
        print("Salvando dicionario")
        with open("dicionario.txt", "w") as fp:
            json.dump(self.dic, fp)  # encode dict into JSON
        print("Dicionario salvo")

    # Print geral para o servidor
    def mostra(self):
        print(self.dic)

    # Verificar existencia de chave
    def contem(self, chave):
        return chave in self.dic

    # Remove chave
    def pop(self, chave):
        self.dic.pop(chave)

    # Adiciona na lista e mantem ordem alfabetica
    def addSort(self, chave, v):
        if self.contem(chave):
            self.dic[chave].append(v)
            self.dic[chave].sort()
        else:
            self.dic[chave] = [v]

    def insert(self, chave, v):
        self.carrega()
        if self.contem(chave):
            log = f"D['{chave}'] já existia, valor '{v}' adicionado"
        else:
            log = f"D['{chave}'] não existia, valor '{v}' adicionado"
        self.addSort(chave, v)
        self.salva()
        return log

    def read(self, chave):
        self.carrega()
        if self.contem(chave):
            log = f"D['{chave}']={self.dic.get(chave)}"
        else:
            log = f"D['{chave}']=[]"
        return log

    def remove(self, chave):
        if self.contem(chave):
            self.pop(chave)
            self.salva()
            log = f"Chave '{chave}' removida."
        else:
            log = f"Chave '{chave}' inexistente."
        return log

    # Consulta valor em chave
    def get(self, chave):
        return self.dic[chave]


class DicionarioRemoto(rpyc.Service):
    """Classe que oferece operacoes matematicas basicas"""

    def __init__(self):
        self.dic = Dicionario()
        self.dic.carrega()

    def on_connect(self, conx):
        print("Conexao estabelecida.")

    def on_disconnect(self, conx):
        print("Conexao encerrada.")

    def exposed_escrita(self, chave, conteudo):
        lock.acquire()
        log = self.dic.insert(chave, conteudo)
        lock.release()
        print(log)
        return log

    def exposed_consulta(self, chave):
        lock.acquire()
        log = self.dic.read(chave)
        lock.release()
        print(log)
        return log

    def exposed_remocao(self, chave):
        lock.acquire()
        log = self.dic.remove(chave)
        lock.release()
        print(log)
        return log


print("Servidor iniciado, esperando conexões!")
dicionarioRemoto = ThreadedServer(DicionarioRemoto, port=10000)
dicionarioRemoto.start()
