# DRISHTI-SHIELD V5

**AI-Powered Satellite Intelligence Platform for Real-Time Border Monitoring**

DRISHTI-SHIELD V5 is a sophisticated geospatial intelligence platform that provides real-time satellite surveillance and automatic anomaly detection for border security and military operations.

## 🚀 Features

- **Real-Time Monitoring**: Live satellite surveillance with automatic 10-second interval checks
- **Automatic Anomaly Detection**: AI-powered detection using advanced change detection algorithms
- **Interactive Map Interface**: Professional geospatial interface with Leaflet.js integration
- **Threat Level Classification**: Automatic classification of detected anomalies (HIGH/MEDIUM/LOW)
- **Live Alert System**: Immediate popup notifications for urgent threat detections
- **Multiple Location Support**: Pre-configured monitoring for Wagah Border, Line of Control, and custom locations
- **Real-Time Intelligence Reports**: AI-generated military-style intelligence summaries
- **Professional UI**: Modern dark theme interface built with Tailwind CSS

## 🛡️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js (optional, for development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bytes06runner/DRISHTI_SHIELD_V5.git
cd DRISHTI_SHIELD_V5
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python api_server.py
```

4. **Access the interface**
Open your browser and navigate to `http://localhost:8000`

## 🗂️ Project Structure

```
DRISHTI-SHIELD-V5/
├── api_server.py              # FastAPI backend with real-time monitoring
├── frontend/
│   └── index.html            # Real-time monitoring interface
├── src/
│   ├── pipeline/
│   │   ├── change_detection.py    # Advanced SSIM-based change detection
│   │   └── report_generator.py    # AI intelligence report generation
│   └── utils/
│       └── geo_utils.py           # Geospatial coordinate conversion
├── data/                         # Simulation satellite imagery
├── static/                       # Generated analysis outputs
└── requirements.txt              # Python dependencies
```

## 🔧 Core Technologies

- **Backend**: FastAPI, OpenCV, scikit-image
- **Frontend**: Vanilla JavaScript, Leaflet.js, Tailwind CSS
- **AI/ML**: SSIM-based change detection, automatic threat classification
- **Geospatial**: Rasterio, GeoJSON processing
- **Real-Time**: WebSocket-ready architecture for live monitoring

## 🎯 Usage

### Real-Time Monitoring
1. Select a monitoring location (Wagah Border, Line of Control, or Custom)
2. Click "Start Monitoring" to begin automatic surveillance
3. The system will check for changes every 10 seconds
4. Immediate alerts will appear for any detected anomalies

### Manual Analysis
1. Click "Check Now" for immediate satellite analysis
2. View detailed results in the analysis panel
3. Examine anomaly markers on the interactive map
4. Access full intelligence reports via the "View Full LLM Report" button

## 🌟 Key Components

### Real-Time Change Detection
Advanced SSIM (Structural Similarity Index) algorithm for robust change detection between satellite image pairs.

### Automatic Threat Classification
Intelligent classification system that categorizes detected anomalies:
- **HIGH**: Large structures/vehicles requiring immediate attention
- **MEDIUM**: Military equipment or personnel movement
- **LOW**: Minor activities for routine monitoring

### Live Alert System
Immediate popup notifications for urgent threat detections with automatic dismissal and threat level indicators.

### Geospatial Intelligence
Professional coordinate conversion and GeoJSON processing for precise anomaly location mapping.

## 📋 API Endpoints

- `GET /` - Main application interface
- `POST /api/v1/analyze_aoi` - Upload and analyze satellite image pairs
- `POST /api/v1/analyze_aoi/monitor` - Real-time monitoring endpoint

## 🔒 Security Features

- Real-time threat assessment with risk scoring (0-10 scale)
- Military-grade intelligence report generation
- Secure file handling and temporary data cleanup
- Professional logging and error tracking

## 🚀 Deployment Ready

This version is optimized for:
- Vercel deployment
- Production environments
- Scalable real-time monitoring
- Professional military/security applications

## 📊 Performance

- Sub-second change detection processing
- Real-time map updates
- Efficient memory management
- Optimized for continuous monitoring operations

## 🤝 Contributing

This project represents advanced geospatial intelligence capabilities suitable for defense and security applications.

## 📄 License

Professional geospatial intelligence platform - All rights reserved.

---

**DRISHTI-SHIELD V5** - Advanced AI-Powered Satellite Intelligence Platform
