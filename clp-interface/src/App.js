import { useState, useEffect } from "react";
import io from "socket.io-client";
import DynamicChart from "./components/DynamicChart";

const socket = io("http://localhost:5001");

export default function ClpDashboard() {
  const [dados, setDados] = useState({ h1: 0, h2: 0, h3: 0, modo: "Automático" });
  const [manual, setManual] = useState(false);
  const [q1, setQ1] = useState("0.000");
  const [q2, setQ2] = useState("0.000");
  const [q3, setQ3] = useState("0.000");
  
  // Histórico dos valores
  const [historicoH, setHistoricoH] = useState({ h1: [], h2: [], h3: [], timestamp: [] });

  useEffect(() => {
    socket.on("update_data", (data) => {
      setDados({ h1: parseFloat(data.h1) || 0, h2: parseFloat(data.h2) || 0, h3: parseFloat(data.h3) || 0 });
      
      if (!manual) {
        setQ1(parseFloat(data.q1)?.toFixed(3) || "0.000");
        setQ2(parseFloat(data.q2)?.toFixed(3) || "0.000");
        setQ3(parseFloat(data.q3)?.toFixed(3) || "0.000");
      }

      // Garantindo valores numéricos no histórico
      setHistoricoH((prev) => ({
        h1: [...prev.h1.slice(-19), parseFloat(data.h1).toFixed(2)],
        h2: [...prev.h2.slice(-19), parseFloat(data.h2).toFixed(2)],
        h3: [...prev.h3.slice(-19), parseFloat(data.h3).toFixed(2)],
        timestamp: [...prev.timestamp.slice(-19), new Date(data.hora).toLocaleTimeString()]
      }));
    });

    return () => socket.off("update_data");
  }, [manual]);

  const enviarComando = () => {
    socket.emit("set_qin", { q1: parseFloat(q1), q2: parseFloat(q2), q3: parseFloat(q3) });
  };

  const alternarModo = () => {
    const novoModo = !manual;
    setManual(novoModo);
    socket.emit("set_manual", novoModo);
  };

  return (
    <div className="flex flex-col items-center p-10 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold">Nível dos Tanques</h1>
      <div className="flex mt-5">
        <div className="p-5 bg-white rounded-lg shadow-md flex flex-col items-center">
          <div className="flex gap-5">
            {[dados.h1, dados.h2, dados.h3].map((h, i) => (
              <div
                key={i}
                className="relative w-24 h-40 flex items-end justify-center border border-gray-500"
                style={{ clipPath: "polygon(100% 0%, 0% 0%, 25% 100%, 75% 100%)" }}
              >
                <div
                  className="bg-blue-500 w-full transition-all"
                  style={{ height: `${h * 100}px` }}
                ></div>
                <span className="absolute bottom-2 text-black text-sm">h{i + 1}={h.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="ml-5 p-5 bg-white rounded-lg shadow-md">
          <h2 className="text-lg font-bold mb-2">Modo</h2>
          <div className="flex items-center gap-2">
            <span>Automático</span>
            <label className="relative inline-flex cursor-pointer">
              <input type="checkbox" checked={manual} onChange={alternarModo} className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-300 peer-checked:bg-blue-600 rounded-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
            </label>
            <span>Manual</span>
          </div>
          <div className="mt-3">
            {[{ label: "Qin Tanque 1", value: q1, set: setQ1 }, { label: "Qin Tanque 2", value: q2, set: setQ2 }, { label: "Qin Tanque 3", value: q3, set: setQ3 }].map((item, i) => (
              <div key={i} className="mb-2">
                <label className="block text-sm">{item.label}</label>
                <input type="number" className="border p-2 w-full rounded-md" value={item.value} onChange={(e) => item.set(e.target.value)} disabled={!manual} />
              </div>
            ))}
          </div>
          <button
            onClick={enviarComando}
            className={`mt-4 w-full py-2 rounded-lg font-bold ${
              manual ? "bg-yellow-500 hover:bg-yellow-600 text-white" : "bg-gray-300 text-gray-500 cursor-not-allowed"
            }`}
            disabled={!manual}
          >
            Aplicar Fluxos
          </button>
        </div>
      </div>
    </div>
  );
}