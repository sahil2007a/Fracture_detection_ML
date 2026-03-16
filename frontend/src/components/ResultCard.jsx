import React from "react";

function ResultCard({ label, value }) {
  if (!value || value === "N/A") return null;
  return (
    <div className="result-card">
      <span className="result-label">{label}</span>
      <span className="result-value">{value}</span>
    </div>
  );
}

export default ResultCard;