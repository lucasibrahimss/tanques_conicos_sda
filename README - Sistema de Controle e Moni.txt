README - Sistema de Controle e Monitoramento de Nível de Tanques

Este sistema simula o comportamento de tanques de fluidos e permite o controle remoto e monitoramento dos níveis de fluido. Ele é composto por vários módulos que interagem entre si, incluindo simulação do comportamento dos tanques, controle PID, comunicação via OPC UA, e comunicação TCP/IP.

Requisitos

Antes de iniciar, é necessário instalar as seguintes bibliotecas no seu ambiente:

pip install socket threading matplotlib numpy opcua

Configuração

1. Endereço do Servidor OPC UA
   Para garantir que o sistema se comunique com o servidor OPC UA corretamente, você deve modificar o endereço do servidor nas variáveis 'OPC_SERVER_URL' localizadas nos seguintes arquivos:

   - tanques_simulacao.py
   - clp.py
   - mes.py

   Altere o valor da variável 'OPC_SERVER_URL' para o endereço de seu servidor OPC UA.

Execução dos Módulos

O sistema é composto por vários scripts que devem ser executados em ordem para garantir o funcionamento adequado:

1. Iniciar a Simulação do Tanque
   Execute o script 'tanques_simulacao.py', que irá simular o comportamento dinâmico dos tanques de fluido e aplicar o controle PID. Este script também gerencia a comunicação com o servidor OPC UA.

   python tanques_simulacao.py

2. Iniciar o CLP 
   Em seguida, execute o script 'clp.py'. Este programa cria o cliente OPC UA, que começará a ler os dados do servidor. Além disso, ele inicializa o servidor TCP/IP e começa a aguardar por uma conexão do cliente.

   python clp.py

3. Iniciar o Cliente TCP/IP
   Depois, execute o script 'cliente.py'. Este programa irá atuar como o cliente TCP/IP, recebendo dados do servidor e exibindo o gráfico do nível dos tanques. Ele também gerará um arquivo 'historiador.txt' onde os dados serão armazenados.

   Durante a execução, você pode interagir com o programa por meio dos seguintes comandos no terminal:

   - Operação Manual:
     Para alternar entre operação automática e manual, use o comando:

     manual,<true/false>

     Exemplo: manual,true ativa a operação manual.

   - Alteração da Vazão:
     Para ajustar as vazões dos tanques, use o comando:

     qi,<q_in1>,<q_in2>,<q_in3>

     Exemplo: qi,1,2,3 define as vazões das válvulas.

     Esse comando exige que o modo manual esteja ativo para ser executado

   python cliente.py

4. Iniciar o MES (Sistema de Execução de Manufatura)
   Por fim, execute o script 'mes.py'. Este programa irá salvar os dados lidos do servidor OPC UA em um arquivo chamado 'mes.txt', permitindo o armazenamento contínuo dos dados para análise posterior.

   python mes.py

Arquivos Gerados

Durante a execução, dois arquivos principais serão gerados:

- 'historiador.txt': Armazena os dados do nível dos tanques para análise.
- 'mes.txt': Contém os dados lidos do servidor OPC UA, registrados pelo MES.

Observações Finais

- A ordem de execução dos scripts é importante para garantir que todos os módulos interajam corretamente.
- Certifique-se de que os endereços do servidor OPC UA estejam corretamente configurados antes de iniciar a execução.
