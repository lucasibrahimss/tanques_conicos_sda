const net = require("net");
const io = require("socket.io")(5001, {
    cors: {
      origin: "http://localhost:3000", // Permitir React acessar WebSocket
      methods: ["GET", "POST"]
    }
  });

// Conectar ao CLP via TCP/IP
const clpClient = new net.Socket();
clpClient.connect(65432, "127.0.0.1", () => {
  console.log("✅ Conectado ao servidor TCP/IP do CLP!");
});

clpClient.on("data", (data) => {
    const message = data.toString();
    console.log("📡 Dados recebidos do CLP:\n", message);
  
    const clpData = parseClpMessage(message);
    
    console.log("📤 Enviando dados para WebSocket:", clpData); // <- ADICIONADO
    
    io.emit("update_data", clpData);
  });

// Manipular erros de conexão
clpClient.on("error", (err) => {
  console.error("❌ Erro na conexão TCP/IP:", err);
});

// Função para converter a string do CLP para JSON
function parseClpMessage(message) {
    const linhas = message.split("\n"); // Divide a mensagem por linha
    let data = { h1: 0, h2: 0, h3: 0, q1: 0, q2: 0, q3: 0, modo: "Automático" };
  
    linhas.forEach((linha) => {

      if (linha.includes("Niveis:")) {
        const niveis = linha.match(/H1=([\d.]+), H2=([\d.]+), H3=([\d.]+)/);
        if (niveis) {
          data.h1 = parseFloat(niveis[1]);
          data.h2 = parseFloat(niveis[2]);
          data.h3 = parseFloat(niveis[3]);
          data.hora = new Date();
        }
      }
      if (linha.includes("Vazoes:")) {
        const vazoes = linha.match(/Q1=([\d.]+), Q2=([\d.]+), Q3=([\d.]+)/);
        if (vazoes) {
          data.q1 = parseFloat(vazoes[1]);
          data.q2 = parseFloat(vazoes[2]);
          data.q3 = parseFloat(vazoes[3]);
        }
      }
      if (linha.includes("Modo:")) {
        data.modo = linha.split("Modo: ")[1].trim();
      }
    });
  
    return data;
  }

// 🔥 NOVO: Enviar comandos do frontend para o CLP
io.on("connection", (socket) => {
  console.log("🔗 Novo cliente conectado:", socket.id);

  // Receber comando para mudar modo manual/automático
  socket.on("set_manual", (manual) => {
    const command = `manual,${manual}`;
    console.log(`🔧 Enviando comando ao CLP: ${command}`);
    clpClient.write(command + "\n");
  });

  // Receber comando para definir vazões
  socket.on("set_qin", ({ q1, q2, q3 }) => {
    const command = `qi,${q1},${q2},${q3}`;
    console.log(`💧 Enviando comando ao CLP: ${command}`);
    clpClient.write(command + "\n");
  });

  socket.on("disconnect", () => {
    console.log("❌ Cliente desconectado:", socket.id);
  });
});

console.log("🚀 Servidor WebSocket rodando na porta 5001...");
