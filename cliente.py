import socket
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re

# Configuração do servidor TCP
SERVER_HOST = "localhost"  # Altere para o IP do servidor, se necessário
SERVER_PORT = 65432        # Mesma porta usada pelo servidor TCP/IP

# Listas para armazenar os valores de h1, h2 e h3 ao longo do tempo
tempo = []
h1_vals = []
h2_vals = []
h3_vals = []
contador = 0  # Contador de tempo para o eixo X

def registrar_mensagem(mensagem):
    """Salva a mensagem recebida no arquivo de log."""
    with open("historiador.txt", "a") as arquivo:
        arquivo.write(f"{mensagem}\n")
        
def processar_mensagem(mensagem):
    """Extrai os valores de H1, H2 e H3 da mensagem recebida."""
    global contador
    try:
        if mensagem.startswith("Hora"):
            registrar_mensagem(mensagem)  # Salva a mensagem no arquivo
        else:
            print(mensagem)
        # Expressão regular para encontrar os valores de H1, H2 e H3
        match = re.search(r"H1=(-?\d+\.\d+), H2=(-?\d+\.\d+), H3=(-?\d+\.\d+)", mensagem)
        if match:
            h1 = float(match.group(1))
            h2 = float(match.group(2))
            h3 = float(match.group(3))

            # Adiciona os valores às listas para plotagem
            tempo.append(contador)
            h1_vals.append(h1)
            h2_vals.append(h2)
            h3_vals.append(h3)
            contador += 1  # Atualiza o tempo
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

def receber_mensagens(client_socket):
    """Thread para receber mensagens do servidor e atualizar os dados."""
    while True:
        try:
            response = client_socket.recv(1024).decode("utf-8")
            processar_mensagem(response)
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def tcp_client():
    """Função principal do cliente TCP."""
    print("Cliente TCP iniciado.")
    print("Conectando ao servidor...")

    try:
        # Criar o socket do cliente
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
            
            # Criar uma thread para receber mensagens
            thread_receber = threading.Thread(target=receber_mensagens, args=(client_socket,))
            thread_receber.daemon = True
            thread_receber.start()

            # Ler comando do usuário
            while True:
                comando = input("Digite um comando (ou 'sair' para encerrar): ").strip()
                if comando.lower() == "sair":
                    print("Encerrando cliente...")
                    break

                client_socket.sendall(comando.encode("utf-8"))
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor. Certifique-se de que ele está em execução.")
    except Exception as e:
        print(f"Erro no cliente TCP: {e}")

def atualizar_grafico(frame):
    """Função para atualizar o gráfico dinamicamente."""
    plt.cla()  # Limpa o gráfico anterior
    
    if tempo:  # Só plota se houver dados
        plt.plot(tempo, h1_vals, label="h1", color='b')
        plt.plot(tempo, h2_vals, label="h2", color='r')
        plt.plot(tempo, h3_vals, label="h3", color='g')
        plt.legend()
    
    plt.xlabel("Tempo")
    plt.ylabel("Altura dos tanques")
    plt.title("Níveis dos Tanques em Tempo Real")
    plt.grid()

if __name__ == "__main__":
    # Iniciar o cliente TCP em uma thread separada
    thread_cliente = threading.Thread(target=tcp_client)
    thread_cliente.start()

    # Criar e exibir o gráfico dinâmico
    fig = plt.figure()
    ani = animation.FuncAnimation(fig, atualizar_grafico, interval=1000, cache_frame_data=False)
    plt.show()
