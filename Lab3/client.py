# Cliente de calculadora usando RPyC
import rpyc
import re


def instrucoes():
    print("\nBem vindo ao dicionário remoto do Rafael!\n")
    print("São cinco comandos disponíveis para o cliente:")
    print('  -r "chave" -> lê no dicionário')
    print('  -w "chave" "valor" -> escreve no dicionário')
    print('  -rm "chave" -> remove no dicionário')
    print("  -fim -> encerra a conexão")
    print("  -ajuda -> repete as instruções")
    print("Boa diversão!\n")


dic = rpyc.connect("localhost", 10000)
while True:
    comando = input("comando: ")

    if comando == "fim":
        dic.close()
        break

    if comando == "ajuda":
        instrucoes()

    else:
        read_match = re.match(r'^r\s+"(.+)"$', comando)
        write_match = re.match(r'^w\s+"(.+)"\s+"(.+)"$', comando)
        remove_match = re.match(r'^rm\s+"(.+)"$', comando)

        if read_match:
            chave = read_match.group(1)
            log = dic.root.consulta(chave)
            print(log)

        elif write_match:
            chave = write_match.group(1)
            conteudo = write_match.group(2)
            log = dic.root.escrita(chave, conteudo)
            print(log)

        elif remove_match:
            chave = remove_match.group(1)
            log = dic.root.remocao(chave)
            print(log)

        else:
            print('Comando inválido, digite "ajuda" para ler instruções')
