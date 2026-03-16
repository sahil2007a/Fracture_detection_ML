import React from "react";

function LanguageToggle({ lang, onChange }) {
  return (
    <div className="language-toggle">
      <span className="lang-label">Language:</span>
      <button
        className={lang === "en" ? "active" : ""}
        onClick={() => onChange("en")}
      >
        🇬🇧 English
      </button>
      <button
        className={lang === "hi" ? "active" : ""}
        onClick={() => onChange("hi")}
      >
        🇮🇳 हिन्दी
      </button>
    </div>
  );
}

export default LanguageToggle;