import { Line } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";
import { useEffect, useState } from "react";

Chart.register(...registerables);

export default function DynamicChart({ historico, titulo, labels, cores, chaves }) {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [],
  });

  useEffect(() => {
    if (!historico || !historico.timestamp || historico.timestamp.length === 0) {
      setChartData({ labels: [], datasets: [] });
      return;
    }

    setChartData({
      labels: historico.timestamp, // Usa timestamp como eixo X
      datasets: chaves.map((chave, index) => ({
        label: labels[index],
        data: historico[chave] ? historico[chave].map((val) => parseFloat(val) || 0) : [],
        borderColor: cores[index],
        borderWidth: 2,
        fill: false,
      })),
    });
  }, [historico]);

  return (
    <div className="bg-white p-5 rounded-lg shadow-md w-full">
      <h2 className="text-xl font-bold mb-2">{titulo}</h2>
      <Line data={chartData} />
    </div>
  );
}