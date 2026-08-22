# 🪪 Aadhaar Analytics & Predictive Intelligence Portal

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Google Cloud Run](https://img.shields.io/badge/GCP-Cloud_Run-4285F4.svg?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise Multi-Shard Time Series Forecasting, Geospatial Density Mapping, MLOps Drift Detection & Anomaly Alert Portal**

Analyze ~5 Million records across **Enrolment**, **Demographic**, and **Biometric** data shards across 28 canonical Indian States and Union Territories. Features multi-model regressors (XGBoost, LightGBM, Random Forest, Ridge Baseline), PyTorch Deep LSTM Neural Networks, quantile uncertainty forecasting, and a production-grade Streamlit web application.

---

## 🚀 Quickstart

### Local Execution
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated MLOps drift audit
python mlops_pipeline.py

# 3. Launch Streamlit Application
streamlit run app.py
```
Open `http://localhost:8080` or `http://localhost:8501` in your browser.

---

## ☁️ Google Cloud Run Deployment

Deploy directly to **GCP Cloud Run** (Project: `vortex-arena-ai-92843`, Region: `asia-south1`):

### Windows (PowerShell / Command Prompt)
```cmd
deploy_to_gcp.bat
```

### Linux / macOS
```bash
chmod +x deploy_to_gcp.sh
./deploy_to_gcp.sh
```

### Manual `gcloud` Command
```bash
gcloud config set project vortex-arena-ai-92843

gcloud run deploy aadhaar-analytics-app \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

---

## 🐳 Docker Deployment

### Build & Run Container
```bash
# Build Docker image
docker build -t aadhaar-analytics-app .

# Run container on port 8080
docker run -p 8080:8080 aadhaar-analytics-app
```

---

## 📌 Features & Dashboard Modules

The Streamlit portal ([`app.py`](file:///c:/aadhar%20hackathon/app.py)) includes **5 interactive modules**:

1. **📊 Executive Dashboard**: High-level KPI metrics, national daily multi-shard time series trends, top 10 state volume rankings, age demographics share pie charts, and **CSV Data Exporters**.
2. **🗺️ Geospatial & EDA**: Interactive **State Centroid GIS Density Map**, Day-of-week seasonality box plots, and cross-shard correlation matrix heatmaps.
3. **🤖 ML Model Leaderboard & MLOps Drift**: Performance leaderboard table (R², RMSE, MAE, MAPE across XGBoost, LightGBM, Random Forest, Ridge, PyTorch LSTM), model comparison charts, and **MLOps KS-test & PSI Feature Drift Status**.
4. **🔮 Live Forecast Predictor (Quantile Bounds)**: Real-time inference engine with **Quantile Uncertainty Bounds** (P10 lower bound, P50 median forecast, P90 upper bound) providing shaded forecast confidence intervals for any state and model.
5. **🚨 Anomaly Alert Engine**: Rolling Z-score anomaly detector flagging campaign volume spikes with an **Automated Webhook Payload Alert Dispatch Simulator** (Slack/Email/PagerDuty integration) and downloadable **Anomaly Log CSV Exporters**.

---

## 📓 Standalone Self-Contained Notebooks (`.ipynb`)

All notebooks are 100% self-contained and run standalone without external script dependencies:

- [`01_Exploratory_Data_Analysis.ipynb`](file:///c:/aadhar%20hackathon/01_Exploratory_Data_Analysis.ipynb): Data ingestion, state canonical normalization, and interactive Plotly visualizations.
- [`02_Model_Training_and_Evaluation.ipynb`](file:///c:/aadhar%20hackathon/02_Model_Training_and_Evaluation.ipynb): 37-feature engineering pipeline, model training (XGBoost, LightGBM, Random Forest, Ridge), metric evaluation, and exporting `.pkl` files to `pkl_models/`.
- [`03_LSTM_Time_Series_Forecasting.ipynb`](file:///c:/aadhar%20hackathon/03_LSTM_Time_Series_Forecasting.ipynb): PyTorch stacked `AadhaarLSTMNetwork`, Huber loss, sequence DataLoader, log-variance stabilization, and model weight exporting.

---

## 📁 Repository Structure

```
c:/aadhar hackathon/
├── app.py                      # Production-grade Streamlit Web Application
├── Dockerfile                  # Cloud Run & Docker Containerization Manifest
├── .dockerignore               # Docker build ignore file
├── Procfile                    # Cloud PaaS deployment entry point
├── requirements.txt            # Pinned Python dependencies
├── mlops_pipeline.py           # Automated MLOps KS & PSI Drift Detection Script
├── deploy_to_gcp.bat           # One-click Windows GCP Cloud Run deploy script
├── deploy_to_gcp.sh            # One-click Linux/macOS GCP Cloud Run deploy script
├── PROJECT_REPORT.md           # Comprehensive technical report & future roadmap
├── README.md                   # Project documentation
├── .streamlit/
│   └── config.toml             # Streamlit server & dark theme configuration
├── pkl_models/                 # Unified model artifacts & metadata JSON directory
│   ├── baseline_ridge_model.pkl
│   ├── best_model.pkl
│   ├── lightgbm_model.pkl
│   ├── random_forest_model.pkl
│   ├── ridge_baseline_model.pkl
│   ├── xgboost_model.pkl
│   ├── lstm_model.pt
│   ├── feature_metadata.json
│   ├── model_comparison.json
│   ├── model_report.json
│   └── mlops_drift_report.json
├── 01_Exploratory_Data_Analysis.ipynb
├── 02_Model_Training_and_Evaluation.ipynb
├── 03_LSTM_Time_Series_Forecasting.ipynb
├── api_data_aadhar_enrolment/   # Enrolment data shard
├── api_data_aadhar_demographic/ # Demographic update data shard
└── api_data_aadhar_biometric/   # Biometric update data shard
```

---

## ⚙️ MLOps & Continuous Monitoring (`mlops_pipeline.py`)

The platform implements continuous feature monitoring:
- **Kolmogorov-Smirnov (KS) Test**: Evaluates statistical distribution divergence between reference baseline and incoming production data.
- **Population Stability Index (PSI)**: Quantifies shift magnitude (< 0.1: Stable, 0.1–0.25: Moderate Shift, > 0.25: Critical Shift requiring retraining).

Run the automated MLOps audit:
```bash
python mlops_pipeline.py
```
*Outputs JSON report to `pkl_models/mlops_drift_report.json`.*

---

## 📄 Technical Report

For in-depth mathematical formulations, feature descriptions, benchmark tables, and future architectural roadmaps, consult [`PROJECT_REPORT.md`](file:///c:/aadhar%20hackathon/PROJECT_REPORT.md).

---

## 📄 License

MIT License - Built for UIDAI Aadhaar Hackathon & Enterprise Predictive Intelligence.
