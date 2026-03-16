# AI X-Ray Fracture Analysis Platform 🦴🔬

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-8.0+-0095D5?style=for-the-badge&logo=ultralytics)](https://ultralytics.com)

**Upload X-ray images or radiology reports for AI-powered fracture detection, annotated visualizations, medical explanations in English & Hindi, and structured analysis.**

- 🚀 **Real-time YOLOv8 fracture detection** with confidence scores
- 📝 **OCR + NLP analysis** of radiology reports
- 🌐 **Hindi translation** for better accessibility
- 🖼️ **Annotated output images** with bounding boxes & labels
- ⚡ **Production-ready FastAPI backend** with automatic model pre-loading

## ✨ Features
| Feature | Backend | Frontend |
|---------|---------|----------|
| Upload X-ray image | ✅ YOLOv8 detection | ✅ Drag-drop UI |
| Upload report image | ✅ OCR + NLP | ✅ Preview |
| Annotated results | ✅ Bounding boxes | ✅ Zoom/pan |
| Bilingual reports | ✅ EN/Hindi | ✅ Toggle |
| Live preview | ✅ Static file serving | ✅ Real-time fetch |

## 📋 Prerequisites
- **Python 3.10+** (`python --version`)
- **Node.js 18+** (`node --version`)
- **Git** (to clone if needed)
- ~8GB RAM (for model loading)
- GPU optional (CPU fallback works)

## 🚀 Quick Start (2 Terminals)

### Terminal 1: Backend (API + ML)
```bash
cd backend
# Virtualenv recommended
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Download models if missing (runs automatically)
python download_models.py

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
**Expected**: `http://localhost:8000/docs` (Swagger UI), `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
**Expected**: `http://localhost:3000` (Vite dev server with proxy to backend)

✅ **App ready!** Open [http://localhost:3000](http://localhost:3000) and upload images.

## 🛠️ Detailed Setup

### Backend
1. **Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Dependencies** (~2GB torch/ultralytics):
   ```bash
   pip install -r requirements.txt
   ```

3. **Models** (YOLOv8n + Helsinki-NLP translator):
   ```bash
   python download_models.py  # Auto-downloads if missing
   ```

4. **Run**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - Logs models loading (~30s first time)
   - CORS enabled for frontend
   - Static files: `/outputs/*`, `/uploads/*`
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend
1. **Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Development Server** (proxies `/api` → `localhost:8000`):
   ```bash
   npm run dev  # http://localhost:3000
   ```

3. **Production Build**:
   ```bash
   npm run build  # dist/ folder
   npm run preview
   ```

## 📡 API Reference

| Endpoint | Method | Description | Example Response |
|----------|--------|-------------|------------------|
| `/api/analyze-image` | POST multipart/file | X-ray fracture detection | `{fracture_detected: true, confidence: 0.92, annotated_image: "/outputs/result_xxx.png", explanation_en: "...", explanation_hi: "..."}` |
| `/api/analyze-report` | POST multipart/file | Report OCR + NLP | `{fracture_type: "distal radius", extracted_text: "..."}` |
| `/api/health` | GET | Health check | `{status: "healthy"}` |
| `/outputs/{id}.png` | GET | Annotated images | Image file |

**Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 File Structure
```
project-root/
├── README.md                 # This file
├── backend/                  # FastAPI + ML
│   ├── main.py              # Entry point
│   ├── api/routes.py        # Endpoints
│   ├── ml/                  # YOLOv8, OCR, NLP
│   ├── models/              # Auto-downloaded
│   ├── requirements.txt
│   └── uploads/outputs/     # Persist results
└── frontend/                # React/Vite
    ├── package.json
    ├── src/services/api.js  # Backend calls
    └── vite.config.js       # Proxy config
```

## 🔧 Troubleshooting
- **Port 8000 busy**: `netstat -ano \| findstr :8000` (Windows) → kill process
- **Model download slow**: Check `backend/models/` , run `python download_models.py`
- **CORS errors**: Backend auto-enabled, restart both servers
- **Frontend proxy fail**: api.js uses direct `localhost:8000`, works without proxy
- **Out of memory**: Close apps, use smaller `yolov8n.pt`
- **Windows paths**: Use `venv\Scripts\activate`, no `source`

**Test Health**: `curl http://localhost:8000/api/health`

## 🤝 Contributing
1. Fork & PR
2. Install deps
3. Add tests (`pytest` backend)
4. Update this README

## ⚖️ Disclaimer
**For research/educational use only. Not a substitute for professional medical diagnosis.**

---
**Made with ❤️ for accessible healthcare AI** | [GitHub](https://github.com)
