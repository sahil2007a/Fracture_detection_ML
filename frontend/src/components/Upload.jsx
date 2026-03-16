import React, { useCallback, useRef, useState } from "react";

function Upload({ onUpload, loading, mode }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFile = useCallback((file) => {
    if (!file) return;
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  }, []);

  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      handleFile(file);
    },
    [handleFile]
  );

  const onDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };
  const onDragLeave = () => setDragOver(false);

  const handleSubmit = () => {
    if (selectedFile) onUpload(selectedFile);
  };

  return (
    <div className="upload-section">
      {/* drop zone */}
      <div
        className={`drop-zone ${dragOver ? "drag-over" : ""} ${
          preview ? "has-preview" : ""
        }`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => inputRef.current?.click()}
      >
        {preview ? (
          <img src={preview} alt="Preview" className="preview-img" />
        ) : (
          <div className="drop-placeholder">
            <span className="drop-icon">
              {mode === "image" ? "🩻" : "📄"}
            </span>
            <p>
              Drag &amp; drop your{" "}
              {mode === "image" ? "X-ray image" : "report image"} here
            </p>
            <p className="drop-sub">or click to browse</p>
            <p className="drop-formats">
              Supported: JPG, PNG, BMP, TIFF, WebP
            </p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      {/* action buttons */}
      <div className="upload-actions">
        {preview && (
          <button
            className="btn-outline"
            onClick={() => {
              setPreview(null);
              setSelectedFile(null);
            }}
          >
            Clear
          </button>
        )}
        <button
          className="btn-primary"
          disabled={!selectedFile || loading}
          onClick={handleSubmit}
        >
          {loading ? (
            <>
              <span className="spinner" /> Analyzing…
            </>
          ) : (
            `Analyze ${mode === "image" ? "X-Ray" : "Report"}`
          )}
        </button>
      </div>
    </div>
  );
}

export default Upload;