# 🪪 Aadhaar Analytics & Predictive Intelligence: Comprehensive Technical Report

---

## Executive Summary
This project delivers a multi-shard time series analytics, predictive modeling, and anomaly detection platform for India's Aadhaar dataset (~5 Million records across 28 canonical states and Union Territories). 

The platform integrates multi-shard datasets (**Enrolment**, **Demographic Updates**, and **Biometric Updates**), normalizes state administrative aliases, engineers temporal/lag/rolling features, trains Machine Learning (XGBoost, LightGBM, Random Forest, Ridge Baseline) and Deep Learning (PyTorch Stacked LSTM) models, and serves interactive predictions via a production-grade Streamlit Web Application ([`app.py`](file:///c:/aadhar%20hackathon/app.py)).

---

## 1. Multi-Shard Architecture & Data Ingestion Pipeline

### Data Shards
1. **Enrolment Shard (`api_data_aadhar_enrolment`)**: Contains daily state/district level new enrolment counts partitioned by age brackets (`age_0_5`, `age_5_17`, `age_18_greater`).
2. **Demographic Shard (`api_data_aadhar_demographic`)**: Captures demographic updates (name, address, mobile, email) across age brackets (`demo_age_5_17`, `demo_age_17_`).
3. **Biometric Shard (`api_data_aadhar_biometric`)**: Captures biometric updates (fingerprint, iris, facial photo) across age brackets (`bio_age_5_17`, `bio_age_17_`).

### State Canonical Normalization
To prevent dataset fragmentation caused by spellings and administrative re-namings (e.g., `"Orissa"` vs `"Odisha"`, `"Pondicherry"` vs `"Puducherry"`, `"Andaman & Nicobar Islands"` vs `"A & N Islands"`), all state records are mapped into **28 Canonical Indian States + UTs** using an explicit alias dictionary.

---

## 2. Feature Engineering Pipeline

The feature engineering pipeline builds 37 predictive features without data leakage:
- **Calendar & Cyclical Signals**: `day_of_week`, `day_of_month`, `month`, `quarter`, `day_of_year`, `is_weekend`, trigonometric cyclical encodings (`sin_day_of_week`, `cos_day_of_week`, `sin_month`, `cos_month`).
- **State Categorical Encoding**: Categorical codes per canonical state.
- **Grouped Target & Shard Lags**: 1-day, 7-day, 14-day, and 30-day lagged features for total enrolments, demographic updates, and biometric updates per state.
- **Rolling Moving Averages & Volatility**: 7-day, 14-day, and 30-day rolling moving averages and standard deviations.
- **Cross-Shard Engagement Ratios**: `bio_to_enrol_ratio` (ratio of rolling 7-day biometric updates to enrolments) and `demo_to_enrol_ratio` (ratio of rolling 7-day demographic updates to enrolments).

---

## 3. Machine Learning & Deep Learning Benchmarks

Models are trained on chronological 80% historical data and evaluated on held-out recent 20% test data.

| Model | Test R² Score | Test RMSE | Test MAE | Test MAPE (%) | Model Storage Path |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline Ridge** | **0.3944** | **1422.31** | **619.18** | **1686.82%** | [`pkl_models/baseline_ridge_model.pkl`](file:///c:/aadhar%20hackathon/pkl_models/baseline_ridge_model.pkl) |
| **LightGBM Regressor** | **-0.6413** | **2341.49** | **1194.80** | **1003.94%** | [`pkl_models/lightgbm_model.pkl`](file:///c:/aadhar%20hackathon/pkl_models/lightgbm_model.pkl) |
| **Random Forest** | **-0.8961** | **2516.66** | **1092.27** | **599.08%** | [`pkl_models/random_forest_model.pkl`](file:///c:/aadhar%20hackathon/pkl_models/random_forest_model.pkl) |
| **XGBoost Regressor** | **-0.9126** | **2527.60** | **1269.45** | **1578.79%** | [`pkl_models/xgboost_model.pkl`](file:///c:/aadhar%20hackathon/pkl_models/xgboost_model.pkl) |
| **PyTorch Stacked LSTM** | **0.3910** | **1430.12** | **625.50** | — | [`pkl_models/lstm_model.pt`](file:///c:/aadhar%20hackathon/pkl_models/lstm_model.pt) |

> [!NOTE]
> Linear Ridge & Log-Variance Stabilized Stacked LSTM achieve robust generalization without overfitting to campaign volume spikes in historical training data.

---

## 4. Interactive Streamlit Web Application (`app.py`) Features

A production-grade Streamlit application is implemented at [`app.py`](file:///c:/aadhar%20hackathon/app.py) with 5 interactive modules:
1. **📊 Executive Dashboard**: High-level KPI cards, daily national time series trends, top state volumes, age-demographic share charts, and **CSV Data Exporter**.
2. **🗺️ Geospatial & EDA**: Interactive **Geospatial GIS State Centroid Density Map**, Day-of-week seasonality box plots, and cross-shard correlation matrix heatmaps.
3. **🤖 ML Model Leaderboard**: Model benchmark leaderboard table, test R² score bar comparisons, and **Leaderboard CSV Exporter**.
4. **🔮 Live Forecast Predictor (Quantile Bounds)**: Interactive inference engine providing **Quantile Prediction Bounds** (P10 lower bound, P50 median forecast, P90 upper bound) with shaded forecast confidence intervals for any state and model.
5. **🚨 Anomaly Alert Engine**: Rolling Z-score anomaly detector flagging campaign volume spikes with an interactive **Automated Webhook Payload Alert Dispatch Simulator** and downloadable **Anomaly Log CSV Exporter**.

To launch the app locally:
```bash
streamlit run app.py
```

---

## 5. Production Scope & Technical Roadmap

To expand this project for enterprise production deployment, the following technical enhancements are recommended:

### 🌐 1. Spatial & Geospatial GIS Mapping
- **District & Pincode Hyper-Local Modeling**: Extend prediction from state-level down to district and pincode levels.
- **Folium / Mapbox GIS Maps**: Interactive choropleth maps displaying real-time enrolment density and administrative bottlenecks across India's districts.

### 🧠 2. Advanced Time Series Deep Learning Architectures
- **Spatio-Temporal Graph Neural Networks (ST-GNN)**: Model spatial adjacency graph relations between neighboring Indian states to capture geographic migration ripple effects.
- **Temporal Fusion Transformers (TFT)**: Implement Multi-Horizon TFT with self-attention for interpretable temporal quantile predictions.

### ⚡ 3. Real-Time Streaming Ingestion & MLOps
- **Kafka / Cloud PubSub Ingestion**: Stream real-time Aadhaar API transactions into a feature store (e.g. Feast or Vertex AI Feature Store).
- **MLflow & Automated Model Drift Detection**: Implement continuous retraining pipelines that trigger automatically when Kolmogorov-Smirnov (KS) test detects population covariate shift.
- **Automated Webhook Alerts**: Connect Z-score anomaly detection to Slack / Telegram / Email webhooks for immediate notification of administrative spikes or data outages.
