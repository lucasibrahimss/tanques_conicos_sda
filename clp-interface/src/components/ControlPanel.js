import React, { useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5001");

const ControlPanel = () => {
  const [modoManual, setModoManual] = useState(false);
  const [q1, setQ1] = useState(0);
  const [q2, setQ2] = useState(0);
  const [q3, setQ3] = useState(0);

  const enviarModo = () => {
    socket.emit("set_manual", modoManual ? "true" : "false");
  };

  const enviarFluxos = () => {
    socket.emit("set_qin", { q1, q2, q3 });
  };

  return (
    <div className="p-4 bg-white shadow-lg rounded-xl w-64">
      <h2 className="text-lg font-bold mb-4">Modo</h2>
      <div className="flex justify-between items-center">
        <span>Automático</span>
        <label className="switch">
          <input
            type="checkbox"
            checked={modoManual}
            onChange={() => setModoManual(!modoManual)}
          />
          <span className="slider round"></span>
        </label>
        <span>Manual</span>
      </div>
      <button
        onClick={enviarModo}
        className="mt-2 w-full bg-blue-500 text-white p-2 rounded"
      >
        Aplicar Modo
      </button>

      <h2 className="text-lg font-bold mt-4 mb-2">Fluxos de Entrada</h2>
      <div className="flex flex-col gap-2">
        <input
          type="number"
          step="0.1"
          value={q1}
          onChange={(e) => setQ1(e.target.value)}
          placeholder="Q1"
          className="p-2 border rounded"
        />
        <input
          type="number"
          step="0.1"
          value={q2}
          onChange={(e) => setQ2(e.target.value)}
          placeholder="Q2"
          className="p-2 border rounded"
        />
        <input
          type="number"
          step="0.1"
          value={q3}
          onChange={(e) => setQ3(e.target.value)}
          placeholder="Q3"
          className="p-2 border rounded"
        />
        <button
          onClick={enviarFluxos}
          className="mt-2 w-full bg-green-500 text-white p-2 rounded"
        >
          Aplicar Fluxos
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;