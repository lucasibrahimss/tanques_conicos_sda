import time
import threading
from opcua import Client

# Endereço do servidor OPC UA
OPC_SERVER_URL = "opc.tcp://MatheusPC:53530/OPCUA/SimulationServer"

# Função para registrar as mensagens no arquivo "mes.txt"
def registrar_mensagem(mensagem):
    with open("mes.txt", "a") as arquivo:
        arquivo.write(f"{mensagem}\n")

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
                # Lendo os valores do servidor OPC
                h1 = self.h1_node.get_value()
                h2 = self.h2_node.get_value()
                h3 = self.h3_node.get_value()
                manual = self.manual_node.get_value()
                q_in1 = self.q_in1_node.get_value()
                q_in2 = self.q_in2_node.get_value()
                q_in3 = self.q_in3_node.get_value()

                # Exibindo os dados no console
                print(f"Modo: {'Manual' if manual else 'Automático'} | Níveis: H1={h1:.3f}, H2={h2:.3f}, H3={h3:.3f} | Vazões: Q1={q_in1:.3f}, Q2={q_in2:.3f}, Q3={q_in3:.3f}")
                
                # Formatar a mensagem para salvar no arquivo
                mensagem = (f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Modo: {'Manual' if manual else 'Automatico'} | "
                            f"Niveis: H1={h1:.3f}, H2={h2:.3f}, H3={h3:.3f} | "
                            f"Vazoes: Q1={q_in1:.3f}, Q2={q_in2:.3f}, Q3={q_in3:.3f}")

                # Registrar no arquivo
                registrar_mensagem(mensagem)
                
                # Aguardar um tempo antes de ler novamente
                time.sleep(1)

        except Exception as e:
            print(f"Erro no Cliente OPC: {e}")

        finally:
            self.client.disconnect()

    def parar(self):
        self.rodando = False

# Iniciar o cliente OPC em uma thread
if __name__ == "__main__":
    cliente_opc = ClienteOPC()
    cliente_opc.start()
    
    # O programa ficará em execução até que o cliente seja parado
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrompendo cliente OPC...")
        cliente_opc.parar()
        cliente_opc.join()
