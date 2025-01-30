import React from "react";

const Tank = ({ level, label }) => {
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-40 bg-gray-300 border-2 border-black rounded-b-lg clip-tank flex items-end justify-center overflow-hidden">
        <div
          className="absolute bottom-0 bg-blue-500 w-full transition-all"
          style={{ height: `${level * 100}%` }}
        />
        <span className="absolute bottom-2 text-black text-sm">{label}={level.toFixed(2)}</span>
      </div>
    </div>
  );
};

export default Tank;