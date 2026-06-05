# Aadhaar Analytics Dashboard

**ML-powered analytics platform for Aadhaar enrollment & update trends across India.**  
Analyzes ~5M records spanning enrollment, demographic, and biometric data — with interactive dashboards, multi-model predictions, anomaly detection, and state-level forecasting.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=flat-square)](https://streamlit.io)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0-9ACD32?style=flat-square)](https://lightgbm.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## Overview

Built for the **UIDAI Aadhaar Hackathon**, this project addresses the challenge of uncovering societal trends in Aadhaar enrollment and update data. The system turns raw government datasets into actionable intelligence — from capacity planning to anomaly response.

**Demo:** [YouTube walkthrough](https://youtu.be/293kr7-k5S4?si=VvmeDya12exBM5JB)

---

## Features

**Dashboard (6 pages)**
- KPIs, actual vs. predicted enrollment, residuals, feature importance, age distribution
- Time-series trends with per-state drill-down
- Geography view: state-level predicted enrollment bar charts
- Anomaly table with context charts
- Forecast slider (30 / 60 / 90 days) with CSV export
- Model report: metrics comparison and top features

**Machine Learning**
- Three trained models: Random Forest, XGBoost, LightGBM
- 60+ engineered features (lags, rolling stats, temporal indicators, volatility, ratios)
- Best model auto-loaded at startup

**Anomaly Detection**
- Z-score + rolling statistics baseline
- Residual-based multi-model consensus
- Severity classification: Low / Medium / High

**Forecasting**
- Recursive 30/60/90-day state-level predictions
- 95% confidence intervals
- Exportable forecast CSV

---

## Model Performance

| Model | R² | RMSE | MAE | Training Time |
|---|---|---|---|---|
| **LightGBM** ⭐ | **0.8276** | 721 | 542 | ~28s |
| XGBoost | 0.8123 | 757 | 578 | ~32s |
| Random Forest | 0.7845 | 892 | 645 | ~45s |

**Top predictive features** (LightGBM): `enrol_rolling_mean_30d`, `days_since_start`, `enrol_lag_7d`, `state_avg_enrol`, `month`

---

## Quickstart

```bash
git clone https://github.com/KunjShah95/aadhar-hackathon1.git
cd aadhar-hackathon1
pip install -r requirements.txt

# Generate models first (run notebook or use pre-trained .pkl files in models/)
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501). Use the sidebar to filter by state, date range, and model.

**To start the Flask prediction API:**

```bash
python backend_api.py
# API available at http://localhost:5000
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check + model info |
| `/predict` | POST | Single enrollment prediction |
| `/predict_batch` | POST | Batch predictions |
| `/model_info` | GET | Full model metadata |

**Example:**

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 3, "month": 6, "enrol_rolling_mean_7d": 1000, ...}'
```

```json
{
  "success": true,
  "prediction": 1247.5,
  "model_used": "LightGBM",
  "confidence_score": 0.8276
}
```

---

## Project Structure

```
aadhar-hackathon1/
├── streamlit_app.py                 # Multi-page Streamlit dashboard
├── aadhar_project_utils.py          # Data loading, feature engineering, models
├── backend_api.py                   # Flask REST API
├── frontend_integration.js          # React/Next.js integration helpers
├── aadhar_trends_analysis.ipynb     # Full analysis notebook (2800+ lines)
├── requirements.txt
│
├── models/
│   ├── best_model.pkl               # LightGBM (auto-loaded)
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── lightgbm_model.pkl
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   ├── feature_metadata.json
│   ├── model_comparison.json
│   └── deployment_info.json
│
├── api_data_aadhar_enrolment/       # ~1M rows
├── api_data_aadhar_demographic/     # ~2M rows
├── api_data_aadhar_biometric/       # ~1.8M rows
│
└── outputs/                         # Auto-generated EDA exports (HTML/CSV)
```

---

## Key Insights

- **Top states** (UP, Bihar, Maharashtra) account for a disproportionate share of enrollments; CV across states is 42%.
- **Age 18+** makes up 55% of enrollments; child enrollment (0–17) is an underserved segment.
- **Mid-week peaks** (Tue–Thu) with ~20% dip on weekends — actionable for staffing.
- **Biometric updates** lag demographic updates (38% vs 62%) — a target for awareness campaigns.
- **847 anomalies** detected (5.2% of data), 22% high-severity — indicating localized campaign spikes or data issues.

---

## Tech Stack

- **Data & ML:** Python 3.8+, Pandas, NumPy, Scikit-learn, XGBoost, LightGBM
- **Dashboard:** Streamlit, Plotly
- **API:** Flask, Flask-CORS
- **Frontend:** TypeScript/React (integration layer)

---

## Deployment

**Docker:**

```bash
docker build -t aadhar-api .
docker run -p 5000:5000 aadhar-api
```

**Cloud (examples):**

```bash
# AWS Elastic Beanstalk
eb init && eb create aadhar-production && eb deploy

# Google Cloud Run
gcloud run deploy aadhar-api --source .
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError: best_model.pkl` | Models not generated | Run the notebook first |
| `ValueError: X has N features, expecting M` | Feature mismatch | Check `feature_metadata.json` |
| `MemoryError` | Dataset too large for RAM | Process in batches; close other apps |
| CORS error from frontend | API URL mismatch | Verify `localhost:5000` in frontend config |

---

## License

MIT — built for the UIDAI Aadhaar Hackathon.

---

## Acknowledgements

- **UIDAI** for dataset availability and problem framing
- Scikit-learn, XGBoost, LightGBM, Streamlit, and Flask open-source communities
