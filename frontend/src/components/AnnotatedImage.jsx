import React, { useState } from "react";

function AnnotatedImage({ src, originalSrc }) {
  const [showOriginal, setShowOriginal] = useState(false);
  const backendBase = "http://localhost:8000";

  const imageSrc = showOriginal
    ? `${backendBase}${originalSrc}`
    : `${backendBase}${src}`;

  return (
    <div className="annotated-image-wrapper">
      <div className="image-toggle-bar">
        <button
          className={!showOriginal ? "active" : ""}
          onClick={() => setShowOriginal(false)}
        >
          🔍 AI Annotated
        </button>
        {originalSrc && (
          <button
            className={showOriginal ? "active" : ""}
            onClick={() => setShowOriginal(true)}
          >
            🖼️ Original
          </button>
        )}
      </div>
      <div className="image-container">
        <img
          src={imageSrc}
          alt={showOriginal ? "Original X-ray" : "Annotated X-ray"}
          className="xray-image"
        />
      </div>
    </div>
  );
}

export default AnnotatedImage;