# **Laboratório 2**
## Aplicação cliente/servidor básica
Sistemas Distribuídos (ICP-367) \
Rafael de Aguiar Ferreira - 117196643 \

___

### **Atividade 1** - Projeto da arquitetura

![image](https://user-images.githubusercontent.com/34279732/236996407-d6d8eaef-e4f4-41e3-8856-3b55fd2b88c2.png)

O projeto conta com vários clientes acessando um servidor. A arquitetura é centralizada, o servidor vai implementar toda a lógica e conterá todos os dados, e os clientes apenas vão mandar executar funções do servidor. A base do estilo arquitetural é o de camadas, 3 camadas: Interface, Processamento e Dados.
A interface é implementada em ambos servidor e cliente, para permitir comandos dos dois lados.
Enquanto a conexão entre a interface-processamento do servidor é direta, a de cliente é mediada por uma conexão TCP (sockets).
Os componentes são: 

**Client Interface** - Fornece informação do programa para o cliente e permite usuário requisitar leitura de uma entrada, ou escrita de uma entrada, ou terminar conexão. 

**Server Interface** - Fornece informação do programa para o servidor e permite usuário requisitar remoção de entrada, ou encerrar servidor (não-imediato, não recebe mais conexões e espera as atuais terminarem).

**Client Request Handler** - Recebe mensagem do cliente, identifica o comando e parâmetros, dispara o comando para o dicionário. 

**Server Request Handler** - Identifica o comando e parâmetros dados pelo servidor, dispara o comando para o dicionário. 

**File with Dictionary** - A base de dados, contém o dicionário em si. É atualizada em toda mudança, na prática é um json e se comunica com open. 

**Feedback Generator** - Recebe as mudanças no dicionário, ou entradas lidas e enviam para as respectivas interfaces que requisitaram. É sensível a se houve êxito nas operações, ou se chave já existia.



### **Atividade 2** - Instancia da Arquitetura em Cliente/Servidor

Como a descrição na atividade 1 já contava com clientes e servidores, no formato de administradores e usuários, partiremos já dela.
O único componente que fica no cliente é o **Client Interface**, que, mais uma vez, se comunica por sockets (especificamente, TCP) com o servidor, mandando requisições e recebendo feedback.

Na prática: o usuário abre o cliente e imediatamente se conecta no servidor, que já possui uma thread em recv() para ele.

A interface fornece as documentação das possíveis requisições e o usuário insere o que quer fazer, ler ou escrever. Ele insere, digamos "read "a"", e essa mensagem é emoldurada por '\n', para separar os comandos em caso de "rajada". Então, o recv por parte do servidor lê a mensagem, faz um match de regex e extrai função e parâmetro.

Desde então, o cliente fica na espera de uma resposta, que pode ser o valor na chave, a lista de valores, ou um comunicado de que a chave não consta.



### **Atividade 3** - Implementação da Arquitetura

