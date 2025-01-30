import threading
import time
import numpy as np
from opcua import Server

OPC_SERVER_URL = "opc.tcp://MatheusPC:53530/OPCUA/SimulationServer"

# Parâmetros dos tanques
R1, R2, R3 = 0.6, 0.7, 0.8  # Raios maiores dos tanques
r1, r2, r3 = 0.3, 0.4, 0.5  # Raios menores dos tanques
H1, H2, H3 = 1.5, 1.8, 2.0  # Altura dos tanques
g1, g2, g3 = 0.4, 0.5, 0.6  # Coeficiente de descarga
h1_0, h2_0, h3_0 = 0, 0, 0        # Níveis iniciais
q_in1, q_in2, q_in3 = 0.2, 0.15, 0.1  # Entradas iniciais
h_r1, h_r2, h_r3 = 1.0, 1.2, 1.5  # Referência de nível para os três tanques
manual = False              # Flag para controle manual

# Inicializar o servidor OPC UA
server = Server()
server.set_endpoint(OPC_SERVER_URL)

# Adicionar nós no servidor OPC UA
namespace = server.register_namespace("Tanques")
tanques = server.nodes.objects.add_object(namespace, "Tanques")
h1_node = tanques.add_variable(namespace, "h1", h1_0)
h2_node = tanques.add_variable(namespace, "h2", h2_0)
h3_node = tanques.add_variable(namespace, "h3", h3_0)
q_in1_node = tanques.add_variable(namespace, "q_in1", q_in1)
q_in2_node = tanques.add_variable(namespace, "q_in2", q_in2)
q_in3_node = tanques.add_variable(namespace, "q_in3", q_in3)
manual_node = tanques.add_variable(namespace, "manual", False)

# Tornar os nós modificáveis
h1_node.set_writable()
h2_node.set_writable()
h3_node.set_writable()
q_in1_node.set_writable()
q_in2_node.set_writable()
q_in3_node.set_writable()
manual_node.set_writable()
manual_node.set_value(False)

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, dt):
        self.Kp = Kp  # Ganho proporcional
        self.Ki = Ki  # Ganho integral
        self.Kd = Kd  # Ganho derivativo
        self.setpoint = setpoint  # Nível desejado do tanque
        self.dt = dt  # Intervalo de tempo entre atualizações
        self.integral = 0  # Termo integral acumulado
        self.ultimo_erro = 0  # Erro na iteração anterior

    def calcular_saida(self, nivel_atual):
        erro = self.setpoint - nivel_atual  # Calcula erro (diferença entre referência e medição)
        self.integral += erro * self.dt  # Acumula erro para ação integral
        derivativo = (erro - self.ultimo_erro) / self.dt  # Calcula ação derivativa
        self.ultimo_erro = erro  # Atualiza erro para próxima iteração

        # Equação do PID
        saida = self.Kp * erro + self.Ki * self.integral + self.Kd * derivativo
        return max(0, saida) 

def modelo_tanques(h, H, q_in, q_next, R, r, gamma):
    area = np.pi * (r + h * (R - r)/H) ** 2  # Área variável com h
    q_out = gamma * np.sqrt(max(h, 0))  # Saída proporcional à raiz de h
    return (q_in - q_out - q_next) / area

# Função para resolver o sistema com Runge-Kutta 4ª ordem  
def runge_kutta(h, H, q_in, q_next, R, r, gamma, dt):
    k1 = modelo_tanques(h, H, q_in, q_next, R, r, gamma)
    k2 = modelo_tanques(h + 0.5 * dt * k1, H, q_in, q_next, R, r, gamma)
    k3 = modelo_tanques(h + 0.5 * dt * k2, H, q_in, q_next, R, r, gamma)
    k4 = modelo_tanques(h + dt * k3, H, q_in, q_next, R, r, gamma)
    novo_nivel = h + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    
    return max(0, min(novo_nivel, H))  # Garantir que o nível não ultrapasse H (altura máxima do tanque)

# Thread dos tanques
class Tanques(threading.Thread):
    def __init__(self):
        super().__init__()
        self.rodando = True
        self.niveis = [h1_0, h2_0, h3_0]
        self.dt = 1  # Passo de tempo (s)

    def run(self):
        while self.rodando:
            q_in = [q_in1_node.get_value(), q_in2_node.get_value(), q_in3_node.get_value()]
            self.niveis[0] = runge_kutta(self.niveis[0], H1, q_in[0], q_in[1], R1, r1, g1, self.dt)
            self.niveis[1] = runge_kutta(self.niveis[1], H2, q_in[1], q_in[2], R2, r2, g2, self.dt)
            self.niveis[2] = runge_kutta(self.niveis[2], H3, q_in[2], 0, R3, r3, g3, self.dt)
            
            # Atualiza os níveis no servidor OPC UA
            h1_node.set_value(self.niveis[0])
            h2_node.set_value(self.niveis[1])
            h3_node.set_value(self.niveis[2])
            
            time.sleep(self.dt)

    def parar(self):
        self.rodando = False
        

# Thread de controle  
class Controle(threading.Thread):
    def __init__(self):
        super().__init__()
        self.rodando = True
        self.dt = 1 
        self.pids = [
            PID(Kp=1.0, Ki=0.1, Kd=0.05, setpoint=h_r1, dt=self.dt),  
            PID(Kp=1.2, Ki=0.15, Kd=0.06, setpoint=h_r2, dt=self.dt),  
            PID(Kp=1.5, Ki=0.2, Kd=0.07, setpoint=h_r3, dt=self.dt)  
        ]

    def run(self):
        while self.rodando:
            modo_manual = manual_node.get_value()
            if modo_manual:
                # Controle manual
                q_in1 = q_in1_node.get_value()
                q_in2 = q_in2_node.get_value()
                q_in3 = q_in3_node.get_value()
                
                q_in1_node.set_value(max(q_in1, 0))  # Evitar valores negativos
                q_in2_node.set_value(max(q_in2, 0))
                q_in3_node.set_value(max(q_in3, 0))
                print(f"Modo Manual - Fluxo Entrada ajustado: q_in1={q_in1}, q_in2={q_in2}, q_in3={q_in3}")
                time.sleep(self.dt)
            else:
                for i in range(3):
                    if i == 0:
                        nivel_atual = h1_node.get_value()
                    elif i == 1:
                        nivel_atual = h2_node.get_value()
                    else:
                        nivel_atual = h3_node.get_value()

                    fluxo_entrada = self.pids[i].calcular_saida(nivel_atual)
                    
                    if i == 0:
                        q_in1_node.set_value(fluxo_entrada)
                    elif i == 1:
                        q_in2_node.set_value(fluxo_entrada)
                    else:
                        q_in3_node.set_value(fluxo_entrada)

                    print(f"Controle PID - Tanque {i+1}: Nível Atual = {nivel_atual:.3f}, Fluxo Entrada = {fluxo_entrada:.3f}")

                time.sleep(self.dt)  # Aguarda o tempo de controle antes da próxima iteração

    def parar(self):
        self.rodando = False
        
if __name__ == "__main__":
    server.start()
    print("Servidor OPC UA iniciado!")

    tanques = Tanques()
    controle = Controle()

    tanques.start()
    controle.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando simulação...")
        tanques.parar()
        controle.parar()

        tanques.join()
        controle.join()

        server.stop()
        print("Simulação finalizada.")