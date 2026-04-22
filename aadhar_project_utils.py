from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
DATA_DIRS = {
    "enrolment": ROOT / "api_data_aadhar_enrolment" / "api_data_aadhar_enrolment",
    "demographic": ROOT / "api_data_aadhar_demographic" / "api_data_aadhar_demographic",
    "biometric": ROOT / "api_data_aadhar_biometric" / "api_data_aadhar_biometric",
}
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "outputs"

CANONICAL_STATES = {
    "andaman and nicobar islands",
    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chandigarh",
    "chhattisgarh",
    "dadra and nagar haveli",
    "dadra and nagar haveli and daman and diu",
    "daman and diu",
    "delhi",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jammu and kashmir",
    "jharkhand",
    "karnataka",
    "kerala",
    "ladakh",
    "lakshadweep",
    "madhya pradesh",
    "maharashtra",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "odisha",
    "puducherry",
    "punjab",
    "rajasthan",
    "sikkim",
    "tamil nadu",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
}

STATE_ALIASES = {
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "andaman and nicobar islands": "Andaman and Nicobar Islands",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhatisgarh": "Chhattisgarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra & nagar haveli": "Dadra and Nagar Haveli",
    "dadra and nagar haveli": "Dadra and Nagar Haveli",
    "dadra and nagar haveli and daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "daman & diu": "Daman and Diu",
    "daman and diu": "Daman and Diu",
    "delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jammu & kashmir": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
}


def _normalize_state_name(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text or text.isdigit():
        return pd.NA
    key = text.lower().replace(".", "").replace(",", "").strip()
    key = key.replace("&", "and")
    key = " ".join(key.split())
    normalized = STATE_ALIASES.get(key, text)
    return normalized if normalized.lower() in CANONICAL_STATES else pd.NA


def _read_csv_shards(folder: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for csv_path in sorted(folder.glob("*.csv")):
        df = pd.read_csv(csv_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        for col in ["state", "district"]:
            if col in df.columns:
                df[col] = df[col].astype("string").str.strip()
        if "state" in df.columns:
            df["state"] = df["state"].map(_normalize_state_name)
            df = df[df["state"].notna()].copy()
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@lru_cache(maxsize=1)
def feature_columns() -> list[str]:
    metadata_path = MODEL_DIR / "feature_metadata.json"
    if metadata_path.exists():
        metadata = pd.read_json(metadata_path, typ="series")
        columns = metadata.get("feature_columns", [])
        if isinstance(columns, list) and columns:
            return columns
    return [
        "day_of_week",
        "month",
        "quarter",
        "day_of_month",
        "is_weekend",
        "is_holiday_month",
        "sin_month",
        "cos_month",
        "sin_day_of_week",
        "cos_day_of_week",
        "lag_1d",
        "lag_7d",
        "lag_14d",
        "lag_30d",
        "rolling_mean_7d",
        "rolling_mean_14d",
        "rolling_mean_30d",
        "rolling_std_7d",
        "rolling_std_14d",
        "rolling_std_30d",
        "state_avg_enrol",
        "state_rank",
        "urban_rural_flag",
        "enrol_to_demographic_ratio",
        "biometric_engagement_score",
        "enrol_growth_7d",
        "enrol_volatility",
        "total_demographic_updates",
        "total_biometric_updates",
    ]


def _aggregate_state_daily(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "state", *value_cols])
    grouped = df.groupby(["date", "state"], as_index=False)[value_cols].sum()
    grouped["state"] = grouped["state"].astype("string")
    return grouped.sort_values(["state", "date"]).reset_index(drop=True)


def _state_urban_flag(state: str) -> int:
    urban_states = {
        "Delhi",
        "Chandigarh",
        "Goa",
        "Puducherry",
        "Lakshadweep",
        "Andaman and Nicobar Islands",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Jammu and Kashmir",
    }
    return int(state in urban_states)


def _safe_rank(series: pd.Series) -> pd.Series:
    return series.rank(method="dense", ascending=False).astype(int)


def build_state_daily_panel() -> pd.DataFrame:
    enrol = _read_csv_shards(DATA_DIRS["enrolment"])
    demographic = _read_csv_shards(DATA_DIRS["demographic"])
    biometric = _read_csv_shards(DATA_DIRS["biometric"])

    enrol_daily = _aggregate_state_daily(enrol, ["age_0_5", "age_5_17", "age_18_greater"])
    if not enrol_daily.empty:
        enrol_daily = enrol_daily.rename(
            columns={
                "age_0_5": "age_0_5",
                "age_5_17": "age_5_17",
                "age_18_greater": "age_18_greater",
            }
        )
        enrol_daily["total_enrolments"] = enrol_daily[["age_0_5", "age_5_17", "age_18_greater"]].sum(axis=1)

    demographic_daily = _aggregate_state_daily(demographic, ["demo_age_5_17", "demo_age_17_"])
    if not demographic_daily.empty:
        demographic_daily["total_demographic_updates"] = demographic_daily[["demo_age_5_17", "demo_age_17_"]].sum(axis=1)

    biometric_daily = _aggregate_state_daily(biometric, ["bio_age_5_17", "bio_age_17_"])
    if not biometric_daily.empty:
        biometric_daily["total_biometric_updates"] = biometric_daily[["bio_age_5_17", "bio_age_17_"]].sum(axis=1)

    panel = enrol_daily[["date", "state", "age_0_5", "age_5_17", "age_18_greater", "total_enrolments"]].copy()
    for other in [
        demographic_daily[["date", "state", "total_demographic_updates"]] if not demographic_daily.empty else pd.DataFrame(),
        biometric_daily[["date", "state", "total_biometric_updates"]] if not biometric_daily.empty else pd.DataFrame(),
    ]:
        if not other.empty:
            panel = panel.merge(other, on=["date", "state"], how="outer")

    panel = panel.sort_values(["state", "date"]).reset_index(drop=True)
    for col in ["age_0_5", "age_5_17", "age_18_greater", "total_enrolments", "total_demographic_updates", "total_biometric_updates"]:
        if col in panel.columns:
            panel[col] = pd.to_numeric(panel[col], errors="coerce").fillna(0.0)

    if panel.empty:
        return panel

    # Build a continuous daily panel per state so lag/rolling features are calendar-aware.
    all_dates = pd.date_range(panel["date"].min(), panel["date"].max(), freq="D")
    states = sorted(panel["state"].dropna().unique().tolist())
    frames: list[pd.DataFrame] = []
    for state in states:
        state_df = panel[panel["state"] == state].set_index("date").reindex(all_dates)
        state_df.index.name = "date"
        state_df["state"] = state
        for col in ["age_0_5", "age_5_17", "age_18_greater", "total_enrolments", "total_demographic_updates", "total_biometric_updates"]:
            if col not in state_df.columns:
                state_df[col] = 0.0
            state_df[col] = pd.to_numeric(state_df[col], errors="coerce").fillna(0.0)
        frames.append(state_df.reset_index())

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.sort_values(["state", "date"]).reset_index(drop=True)

    panel["day_of_week"] = panel["date"].dt.dayofweek.astype(int)
    panel["month"] = panel["date"].dt.month.astype(int)
    panel["quarter"] = panel["date"].dt.quarter.astype(int)
    panel["day_of_month"] = panel["date"].dt.day.astype(int)
    panel["is_weekend"] = panel["day_of_week"].isin([5, 6]).astype(int)
    panel["is_holiday_month"] = panel["month"].isin([10, 11, 12]).astype(int)
    panel["sin_month"] = np.sin(2 * np.pi * panel["month"] / 12)
    panel["cos_month"] = np.cos(2 * np.pi * panel["month"] / 12)
    panel["sin_day_of_week"] = np.sin(2 * np.pi * panel["day_of_week"] / 7)
    panel["cos_day_of_week"] = np.cos(2 * np.pi * panel["day_of_week"] / 7)

    grouped = panel.groupby("state", group_keys=False)
    for lag in [1, 7, 14, 30]:
        panel[f"lag_{lag}d"] = grouped["total_enrolments"].shift(lag)
    for window in [7, 14, 30]:
        panel[f"rolling_mean_{window}d"] = grouped["total_enrolments"].transform(lambda s: s.rolling(window, min_periods=1).mean())
        panel[f"rolling_std_{window}d"] = grouped["total_enrolments"].transform(lambda s: s.rolling(window, min_periods=1).std().fillna(0.0))

    state_avg = panel.groupby("state")["total_enrolments"].mean().sort_values(ascending=False)
    panel["state_avg_enrol"] = panel["state"].map(state_avg).astype(float)
    panel["state_rank"] = panel["state"].map(_safe_rank(state_avg)).astype(int)
    panel["urban_rural_flag"] = panel["state"].map(lambda x: _state_urban_flag(str(x))).astype(int)

    panel["enrol_to_demographic_ratio"] = panel["total_enrolments"] / panel["total_demographic_updates"].replace(0, np.nan)
    panel["enrol_to_demographic_ratio"] = panel["enrol_to_demographic_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    panel["biometric_engagement_score"] = panel["total_biometric_updates"] / panel["total_enrolments"].replace(0, np.nan)
    panel["biometric_engagement_score"] = panel["biometric_engagement_score"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    panel["enrol_growth_7d"] = panel.groupby("state")["total_enrolments"].pct_change(periods=7).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    panel["enrol_volatility"] = panel["rolling_std_30d"].fillna(0.0)

    # Fill early lag gaps with sensible defaults for model consumption.
    for col in [c for c in panel.columns if c.startswith("lag_") or c.startswith("rolling_")]:
        panel[col] = panel.groupby("state")[col].transform(lambda s: s.bfill().ffill().fillna(0.0))

    panel = panel.fillna(0.0)
    return panel


def prepare_model_frame(df: pd.DataFrame, feature_list: list[str] | None = None) -> pd.DataFrame:
    feature_list = feature_list or feature_columns()
    frame = df.copy()
    for feature in feature_list:
        if feature not in frame.columns:
            frame[feature] = 0.0
        frame[feature] = pd.to_numeric(frame[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return frame


def _sanitize_feature_frame(
    frame: pd.DataFrame,
    feature_list: list[str],
    feature_ranges: dict[str, Any] | None = None,
) -> pd.DataFrame:
    sanitized = frame.copy()
    for feature in feature_list:
        if feature not in sanitized.columns:
            sanitized[feature] = 0.0
        sanitized[feature] = pd.to_numeric(sanitized[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
        if feature_ranges and feature in feature_ranges:
            bounds = feature_ranges[feature]
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
                low, high = bounds
                if pd.notna(low) and pd.notna(high):
                    sanitized[feature] = sanitized[feature].clip(lower=float(low), upper=float(high))
    return sanitized


def _load_model_file(path: Path) -> Any:
    try:
        return joblib.load(path)
    except Exception:
        import pickle

        with path.open("rb") as fh:
            return pickle.load(fh)


@lru_cache(maxsize=1)
def load_best_bundle() -> dict[str, Any]:
    metadata_path = MODEL_DIR / "feature_metadata.json"
    report_path = MODEL_DIR / "model_report.json"
    comparison_path = MODEL_DIR / "model_comparison.json"

    feature_metadata = pd.read_json(metadata_path, typ="series").to_dict() if metadata_path.exists() else {}
    model_report = pd.read_json(report_path, typ="series").to_dict() if report_path.exists() else {}
    model_comparison = pd.read_json(comparison_path) if comparison_path.exists() else pd.DataFrame()

    available_models: dict[str, Any] = {}
    candidates = [
        ("XGBoost", MODEL_DIR / "xgboost_model.pkl"),
        ("Random Forest", MODEL_DIR / "random_forest_model.pkl"),
        ("LightGBM", MODEL_DIR / "best_model.pkl"),
        ("Linear Regression", MODEL_DIR / "linear_model.pkl"),
    ]
    for name, path in candidates:
        if path.exists():
            try:
                available_models[name] = _load_model_file(path)
            except Exception:
                continue

    best_name = None
    if not model_comparison.empty and "Model" in model_comparison.columns:
        score_col = "Test R2" if "Test R2" in model_comparison.columns else ("r2" if "r2" in model_comparison.columns else None)
        if score_col:
            best_name = model_comparison.sort_values(score_col, ascending=False).iloc[0]["Model"]
    if best_name not in available_models:
        best_name = next(iter(available_models), None)

    best_model = available_models.get(best_name) if best_name else None
    if best_model is None and available_models:
        best_name, best_model = next(iter(available_models.items()))

    return {
        "best_model": best_model,
        "best_model_name": best_name,
        "available_models": available_models,
        "feature_metadata": feature_metadata,
        "model_report": model_report,
        "model_comparison": model_comparison,
    }


def _predict_frame(model: Any, frame: pd.DataFrame, feature_list: list[str]) -> np.ndarray:
    X = frame[feature_list]
    preds = model.predict(X)
    return np.asarray(preds, dtype=float)


def recursive_forecast_lightgbm(
    model: Any,
    df: pd.DataFrame,
    horizon: int,
    state: str,
    feature_list: list[str],
    scaler: Any | None = None,
    feature_ranges: dict[str, Any] | None = None,
) -> pd.DataFrame:
    history = df[df["state"] == state].sort_values("date").copy()
    if history.empty:
        return pd.DataFrame(columns=["date", "forecast", "state"])

    history = prepare_model_frame(history, feature_list)
    history["predicted"] = _predict_frame(model, history, feature_list)

    last_row = history.iloc[-1].copy()
    state_avg_enrol = float(history["total_enrolments"].mean())
    state_rank = int(history["state_rank"].iloc[-1]) if "state_rank" in history.columns else 1
    urban_flag = int(history["urban_rural_flag"].iloc[-1]) if "urban_rural_flag" in history.columns else _state_urban_flag(state)

    forecast_rows: list[dict[str, Any]] = []
    rolling_history = history["predicted"].tolist()
    demographic_history = history["total_demographic_updates"].tolist()
    biometric_history = history["total_biometric_updates"].tolist()

    for step in range(1, horizon + 1):
        next_date = pd.to_datetime(last_row["date"]) + pd.Timedelta(days=step)
        day_of_week = int(next_date.dayofweek)
        month = int(next_date.month)
        quarter = int(next_date.quarter)
        day_of_month = int(next_date.day)
        is_weekend = int(day_of_week in [5, 6])
        is_holiday_month = int(month in [10, 11, 12])
        sin_month = float(np.sin(2 * np.pi * month / 12))
        cos_month = float(np.cos(2 * np.pi * month / 12))
        sin_day_of_week = float(np.sin(2 * np.pi * day_of_week / 7))
        cos_day_of_week = float(np.cos(2 * np.pi * day_of_week / 7))

        lag_1d = rolling_history[-1] if len(rolling_history) >= 1 else float(last_row["total_enrolments"])
        lag_7d = rolling_history[-7] if len(rolling_history) >= 7 else lag_1d
        lag_14d = rolling_history[-14] if len(rolling_history) >= 14 else lag_7d
        lag_30d = rolling_history[-30] if len(rolling_history) >= 30 else lag_14d
        rolling_mean_7d = float(np.mean(rolling_history[-7:]))
        rolling_mean_14d = float(np.mean(rolling_history[-14:]))
        rolling_mean_30d = float(np.mean(rolling_history[-30:]))
        rolling_std_7d = float(np.std(rolling_history[-7:], ddof=1)) if len(rolling_history) > 1 else 0.0
        rolling_std_14d = float(np.std(rolling_history[-14:], ddof=1)) if len(rolling_history) > 1 else 0.0
        rolling_std_30d = float(np.std(rolling_history[-30:], ddof=1)) if len(rolling_history) > 1 else 0.0
        enrol_growth_7d = float((lag_1d - lag_7d) / abs(lag_7d)) if pd.notna(lag_7d) and lag_7d != 0 else 0.0
        enrol_volatility = rolling_std_30d

        demographic_proxy = float(np.mean(demographic_history[-7:])) if demographic_history else 0.0
        biometric_proxy = float(np.mean(biometric_history[-7:])) if biometric_history else 0.0
        enrol_to_demographic_ratio = float(lag_1d / demographic_proxy) if demographic_proxy else 0.0
        biometric_engagement_score = float(biometric_proxy / lag_1d) if lag_1d else 0.0

        feature_row = {
            "day_of_week": day_of_week,
            "month": month,
            "quarter": quarter,
            "day_of_month": day_of_month,
            "is_weekend": is_weekend,
            "is_holiday_month": is_holiday_month,
            "sin_month": sin_month,
            "cos_month": cos_month,
            "sin_day_of_week": sin_day_of_week,
            "cos_day_of_week": cos_day_of_week,
            "lag_1d": lag_1d,
            "lag_7d": lag_7d,
            "lag_14d": lag_14d,
            "lag_30d": lag_30d,
            "rolling_mean_7d": rolling_mean_7d,
            "rolling_mean_14d": rolling_mean_14d,
            "rolling_mean_30d": rolling_mean_30d,
            "rolling_std_7d": rolling_std_7d,
            "rolling_std_14d": rolling_std_14d,
            "rolling_std_30d": rolling_std_30d,
            "state_avg_enrol": state_avg_enrol,
            "state_rank": state_rank,
            "urban_rural_flag": urban_flag,
            "enrol_to_demographic_ratio": enrol_to_demographic_ratio,
            "biometric_engagement_score": biometric_engagement_score,
            "enrol_growth_7d": enrol_growth_7d,
            "enrol_volatility": enrol_volatility,
            "total_demographic_updates": demographic_proxy,
            "total_biometric_updates": biometric_proxy,
        }
        feature_frame = _sanitize_feature_frame(pd.DataFrame([feature_row]), feature_list, feature_ranges)
        forecast = float(model.predict(feature_frame[feature_list])[0])
        if not np.isfinite(forecast):
            forecast = float(lag_1d)
        forecast = max(0.0, forecast)
        if feature_ranges and "total_enrolments" in feature_ranges:
            bounds = feature_ranges["total_enrolments"]
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2 and pd.notna(bounds[1]):
                forecast = min(forecast, float(bounds[1]))
        forecast_rows.append({"date": next_date, "state": state, "forecast": forecast})
        rolling_history.append(forecast)
        demographic_history.append(demographic_proxy)
        biometric_history.append(biometric_proxy)

    return pd.DataFrame(forecast_rows)


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "state", "total_enrolments", "z_score", "severity"])

    frame = df.sort_values(["state", "date"]).copy()
    frame["rolling_mean_14d"] = frame.groupby("state")["total_enrolments"].transform(lambda s: s.rolling(14, min_periods=1).mean())
    frame["rolling_std_14d"] = frame.groupby("state")["total_enrolments"].transform(lambda s: s.rolling(14, min_periods=1).std().fillna(0.0))
    frame["z_score"] = (frame["total_enrolments"] - frame["rolling_mean_14d"]) / frame["rolling_std_14d"].replace(0, np.nan)
    frame["z_score"] = frame["z_score"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    abs_z = frame["z_score"].abs()
    frame["severity"] = pd.cut(
        abs_z,
        bins=[-0.1, 1.5, 2.5, np.inf],
        labels=["Low", "Moderate", "High"],
        include_lowest=True,
    ).astype(str)
    anomalies = frame[abs_z >= 2.0].copy()
    return anomalies[["date", "state", "total_enrolments", "z_score", "severity"]].sort_values(["z_score"], ascending=False).reset_index(drop=True)


def generate_eda_artifacts(panel: pd.DataFrame) -> list[str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    summary = panel.groupby("date", as_index=False)[["total_enrolments", "total_demographic_updates", "total_biometric_updates"]].sum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=summary["date"], y=summary["total_enrolments"], name="Enrolments"))
    fig.add_trace(go.Scatter(x=summary["date"], y=summary["total_demographic_updates"], name="Demographic updates"))
    fig.add_trace(go.Scatter(x=summary["date"], y=summary["total_biometric_updates"], name="Biometric updates"))
    line_path = OUTPUT_DIR / "eda_totals_over_time.html"
    fig.write_html(line_path)
    paths.append(str(line_path))

    top_states = panel.groupby("state", as_index=False)["total_enrolments"].sum().sort_values("total_enrolments", ascending=False).head(15)
    bar_path = OUTPUT_DIR / "eda_top_states.html"
    px.bar(top_states, x="total_enrolments", y="state", orientation="h", title="Top states by enrolment").write_html(bar_path)
    paths.append(str(bar_path))

    anomaly_path = OUTPUT_DIR / "eda_anomalies.csv"
    detect_anomalies(panel).to_csv(anomaly_path, index=False)
    paths.append(str(anomaly_path))
    return paths
