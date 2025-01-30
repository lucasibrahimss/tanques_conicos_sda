import threading
import socket
import time
from opcua import Client
from datetime import datetime 

# Endereço do servidor OPC UA
OPC_SERVER_URL = "opc.tcp://MatheusPC:53530/OPCUA/SimulationServer"

# Configuração do servidor TCP/IP
TCP_HOST = "0.0.0.0"
TCP_PORT = 65432

# Thread do Cliente OPC
class ClienteOPC(threading.Thread):
    def __init__(self):
        super().__init__()
        self.client = Client(OPC_SERVER_URL)
        self.rodando = True
        self.h1_node = None
        self.h2_node = None
        self.h3_node = None
        self.manual_node = None
        self.q_in1_node = None
        self.q_in2_node = None
        self.q_in3_node = None

    def run(self):
        try:
            self.client.connect()
            print(f"Conectado ao servidor OPC UA em {OPC_SERVER_URL}")
            tanques = self.client.get_objects_node().get_child(["2:Tanques"])
            self.h1_node = tanques.get_child(["2:h1"])
            self.h2_node = tanques.get_child(["2:h2"])
            self.h3_node = tanques.get_child(["2:h3"])
            self.q_in1_node = tanques.get_child(["2:q_in1"])
            self.q_in2_node = tanques.get_child(["2:q_in2"])
            self.q_in3_node = tanques.get_child(["2:q_in3"])
            self.manual_node = tanques.get_child(["2:manual"])
            

            while self.rodando:
                h1 = self.h1_node.get_value()
                h2 = self.h2_node.get_value()
                h3 = self.h3_node.get_value()
                manual = self.manual_node.get_value()
                q_in1 = self.q_in1_node.get_value()
                q_in2 = self.q_in2_node.get_value()
                q_in3 = self.q_in3_node.get_value()
                print(f"Cliente OPC - Modo: {'Manual' if manual else 'Automático'} | Níveis: H1={h1:.3f}, H2={h2:.3f}, H3={h3:.3f} | Vazões: Q1={q_in1:.3f}, Q2={q_in2:.3f}, Q3={q_in3:.3f}")       
                time.sleep(1)

        except Exception as e:
            print(f"Erro no Cliente OPC: {e}")

        finally:
            self.client.disconnect()

    def parar(self):
        self.rodando = False


# Thread do Servidor TCP/IP
class ServidorTCP(threading.Thread):
    def __init__(self, opc_cliente):
        super().__init__()
        self.rodando = True
        self.opc_cliente = opc_cliente
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((TCP_HOST, TCP_PORT))
        self.server_socket.listen(5)
        self.client_sockets = []

    def run(self):
        print(f"Servidor TCP/IP aguardando conexões em {TCP_HOST}:{TCP_PORT}...")

        while self.rodando:
            try:
                conn, addr = self.server_socket.accept()
                print(f"Conexão estabelecida com {addr}")
                
                welcome_message = (
                    b"Bem-vindo ao CLP! Comandos suportados:\n"
                    b"manual,<true/false> - Alterar modo manual\n"
                    b"qi,<q_in1>,<q_in2>,<q_in3> - Alterar vazoes\n"
                )
                conn.sendall(welcome_message)
                
                self.client_sockets.append(conn)
                
                client_thread = threading.Thread(target=self.tratar_cliente, args=(conn,))
                client_thread.start()
            except socket.error:
                break

    def tratar_cliente(self, client_socket):
        try:
            while self.rodando:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break

                print(f"Mensagem recebida: {data}")
                
                data = data.lower().strip()

                if data.startswith("manual"):
                    _, valor = data.split(",", 1)
                    valor = valor.strip()
                    if valor == 'true':
                        self.opc_cliente.manual_node.set_value(True)
                        client_socket.sendall(b"Modo manual ativado.\n")
                    elif valor == 'false':
                        self.opc_cliente.manual_node.set_value(False)
                        client_socket.sendall(b"Modo manual desativado.\n")
                    else:
                        client_socket.sendall(b"Comando invalido para 'manual'.\n")

                elif data.startswith("qi"):
                    manual_mode = self.opc_cliente.manual_node.get_value()
                    if not manual_mode:
                        client_socket.sendall(b"Erro: As vazoes so podem ser alteradas no modo manual.\n")
                    else:
                        try:
                            _, q_str = data.split(",", 1)
                            q_values = [float(q.strip()) for q in q_str.split(",")]
                            if len(q_values) == 3:
                                q1, q2, q3 = q_values
                                self.opc_cliente.q_in1_node.set_value(q1)
                                self.opc_cliente.q_in2_node.set_value(q2)
                                self.opc_cliente.q_in3_node.set_value(q3)
                                client_socket.sendall(b"Vazoes alteradas com sucesso.\n")
                        except ValueError:
                            client_socket.sendall(b"Erro no comando 'qi'.\n")

                else:
                    client_socket.sendall(b"Comando desconhecido.\n")

        except Exception as e:
            print(f"Erro na comunicação com cliente: {e}")
        finally:
            client_socket.close()
            self.client_sockets.remove(client_socket)
            
    def enviar_dados(self):
        while self.rodando:
            try:
                hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for client_socket in self.client_sockets:
                    dados = (
                        f"Hora: {hora_atual}\n"
                        f"Niveis: H1={self.opc_cliente.h1_node.get_value():.3f}, H2={self.opc_cliente.h2_node.get_value():.3f}, H3={self.opc_cliente.h3_node.get_value():.3f}\n"
                        f"Vazoes: Q1={self.opc_cliente.q_in1_node.get_value():.3f}, Q2={self.opc_cliente.q_in2_node.get_value():.3f}, Q3={self.opc_cliente.q_in3_node.get_value():.3f}\n"
                        f"Modo: {'Manual' if self.opc_cliente.manual_node.get_value() else 'Automatico'}\n"
                    )
                    client_socket.sendall(dados.encode('utf-8'))
                time.sleep(1) 
            except Exception as e:
                print(f"Erro ao enviar dados aos clientes: {e}")
                break

    def parar(self):
        self.rodando = False
        self.server_socket.close()


# Iniciar threads
if __name__ == "__main__":
    opc_client_thread = ClienteOPC()
    tcp_server_thread = ServidorTCP(opc_client_thread)

    opc_client_thread.start()
    tcp_server_thread.start()
    
    enviar_dados_thread = threading.Thread(target=tcp_server_thread.enviar_dados)
    enviar_dados_thread.start()

    print("[CLP] Sistema iniciado.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando o sistema...")
        opc_client_thread.parar()
        tcp_server_thread.parar()
