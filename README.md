# 🪪 Aadhaar Analytics Dashboard

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

**ML-Powered Analytics Platform for Aadhaar Enrollment & Updates**  
Analyze ~5M records across enrollment, demographic, and biometric data shards. Features interactive dashboard, predictions (RF/XGBoost/LightGBM), anomaly detection, and state-level forecasting.

## 🎯 Features

- **Multi-Page Dashboard**: KPIs, trends, geography, anomalies, forecasts, model reports.
- **Model Predictions**: Attach forecasts to daily panels; R² up to 0.93 (XGBoost).
- **Anomaly Detection**: Z-score + rolling stats; severity (Low/Mod/High).
- **Forecasting**: Recursive 30/60/90-day state predictions.
- **Visualizations**: Plotly charts (lines, bars, pies) for actual vs predicted.
- **28 Canonical States**: Normalized from raw data aliases.
- **Feature Engineering**: 30+ feats (lags, rollings, temporal, ratios, volatility).

## 🚀 Quickstart

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501). Sidebar: Filter states/dates, select models.

## 📱 Screenshots

### Dashboard (KPIs + Charts)

![Dashboard](outputs/dashboard.png) <!-- Generate via app button -->

### Trends + Forecast

![Trends](outputs/trends.png)

### Model Comparison

| Model | Test R² | RMSE | MAE |
|-------|---------|------|-----|
| XGBoost | 0.929 | 1008 | 175 |
| Random Forest | 0.915 | 1106 | 321 |
| LightGBM | 0.904 | 1176 | 279 |

*(Metrics from `models/model_comparison.json`)*

## 📂 Project Structure

```
c:/aadhar hackathon/
├── streamlit_app.py     # Multi-page Streamlit dashboard
├── aadhar_project_utils.py # Data utils, features, models, forecast, anomalies
├── requirements.txt     # Dependencies
├── TODO.md             # Task progress
├── README.md           # This file
├── models/             # .pkl models + metadata JSNs
│   ├── best_model.pkl
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── feature_metadata.json
│   ├── model_comparison.json
│   └── model_report.json
├── api_data_aadhar_enrolment/   # ~1M rows
├── api_data_aadhar_demographic/ # ~2M rows
├── api_data_aadhar_biometric/   # ~1.8M rows
└── outputs/            # EDA HTMLs/CSVs (auto-generated)
```

## 🔧 Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-orange)
![Pandas](https://img.shields.io/badge/Pandas-2.0-green)
![Plotly](https://img.shields.io/badge/Plotly-5.17-blue)
![LightGBM](https://img.shields.io/badge/LightGBM-4.1-green)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-yellow)

## 📈 Usage

1. **Filters**: Sidebar states/dates.
2. **Models**: Select from available (best auto-loaded).
3. **Pages**:
   - **Dashboard**: KPIs, actual/pred, top states, residuals, features, age pie.
   - **Trends**: TS overview + top-state drill.
   - **Geography**: State bar (predicted enrolments).
   - **Anomalies**: Table + state context chart.
   - **Forecast**: Slider horizon (30/60/90), download CSV.
   - **Model Report**: Metrics table/chart, top features.
4. **Exports**: `outputs/` via `Generate EDA` button.

## 🗺️ Data Processing

- **Shards**: Aggregated to state-daily panels (continuous dates).
- **Normalization**: 28 states (aliases → canonical).
- **Features**: `day_of_week`, `lags_1/7/14/30`, `rolling_mean/std_7/14/30`, ratios, etc.
- **Coverage**: All dates filled; early lags=0.

## 🔮 Key Insights (from App)

- **Concentration**: Top states (UP/Bihar/MP) dominate.
- **Spikes**: Campaign-driven peaks detectable via anomalies.
- **Age**: Strong youth focus.
- **Forecast**: Use for capacity planning.

## 🛠️ Development

- Models trained externally; artifacts in `models/`.
- Extend: Add Prophet/LSTM, district choropleths (Folium), Flask API.
- Cache: `@st.cache_data/resource` for perf.

## 📄 License

MIT - Built for Aadhaar Hackathon.

## 🙏 Acknowledgements

- Libraries: Streamlit, Pandas, Plotly, LightGBM, XGBoost   
- Hackathon: Organized by  UIDAI, inspired by real-world Aadhaar analytics needs.
- Inspiration: Data science dashboards, forecasting, anomaly detection best practices.
