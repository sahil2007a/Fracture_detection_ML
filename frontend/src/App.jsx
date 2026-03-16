import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Results from "./pages/Results";

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);

  return (
    <div className="app-container">
      {/* ── top nav ──────────────────────────────── */}
      <header className="app-header">
        <div className="header-inner">
          <a href="/" className="logo">
            <span className="logo-icon">🦴</span>
            <span className="logo-text">FractureAI</span>
          </a>
          <nav>
            <a href="/">Home</a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      {/* ── routes ───────────────────────────────── */}
      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={<Home onResult={setAnalysisResult} />}
          />
          <Route
            path="/results"
            element={<Results data={analysisResult} />}
          />
        </Routes>
      </main>

      {/* ── footer ───────────────────────────────── */}
      <footer className="app-footer">
        <p>
          AI X-Ray Fracture Analysis Platform &mdash; Research Prototype
          &copy; {new Date().getFullYear()}
        </p>
        <p className="disclaimer">
          ⚠️ This tool is for educational / research purposes only and
          does <strong>not</strong> replace professional medical advice.
        </p>
      </footer>
    </div>
  );
}

export default App;