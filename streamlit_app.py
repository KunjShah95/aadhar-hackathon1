from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from aadhar_project_utils import (
    build_state_daily_panel,
    detect_anomalies,
    feature_columns,
    generate_eda_artifacts,
    load_best_bundle,
    prepare_model_frame,
    recursive_forecast_lightgbm,
)


st.set_page_config(page_title="Aadhaar Analytics Dashboard", page_icon="🪪", layout="wide")


CUSTOM_CSS = """
<style>
.kpi-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
    padding: 1rem 1.2rem;
    border-radius: 14px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.15);
}
.kpi-title { font-size: 0.82rem; opacity: 0.82; margin-bottom: 0.2rem; }
.kpi-value { font-size: 1.7rem; font-weight: 700; line-height: 1.1; }
.kpi-subtitle { font-size: 0.8rem; opacity: 0.75; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_panel() -> pd.DataFrame:
    return build_state_daily_panel()


@st.cache_resource(show_spinner=False)
def load_artifacts():
    return load_best_bundle()


@st.cache_data(show_spinner=False)
def load_anomalies() -> pd.DataFrame:
    return detect_anomalies(load_panel())


panel = load_panel()
bundle = load_artifacts()
anomalies = load_anomalies()
model_report = bundle.get("model_report", {})
model_comparison = bundle.get("model_comparison", pd.DataFrame())
metadata = bundle.get("feature_metadata", {})
feature_list = metadata.get("feature_columns", feature_columns())
available_models = bundle.get("available_models", {})
best_model_name = bundle.get("best_model_name")


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    states = sorted(df["state"].dropna().unique().tolist())
    default_states = states
    selected_states = st.sidebar.multiselect("States", states, default=default_states)
    date_range = st.sidebar.date_input(
        "Date range",
        value=(df["date"].min().date(), df["date"].max().date()),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )
    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date, end_date = df["date"].min().date(), df["date"].max().date()
    filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()
    if selected_states:
        filtered = filtered[filtered["state"].isin(selected_states)]
    return filtered


def selected_model_sidebar() -> tuple[str, object | None]:
    st.sidebar.header("Models")
    model_names = list(available_models.keys())
    if not model_names:
        st.sidebar.error("No compatible model artifacts were loaded.")
        return "", None
    default_index = model_names.index(best_model_name) if best_model_name in model_names else 0
    selected_name = st.sidebar.selectbox("Choose model", model_names, index=default_index)
    return selected_name, available_models[selected_name]


def get_feature_importance(model: object) -> pd.DataFrame:
    if hasattr(model, "feature_importances_"):
        values = np.asarray(getattr(model, "feature_importances_"), dtype=float)
        return pd.DataFrame({"feature": feature_list[: len(values)], "importance": values}).sort_values("importance", ascending=False)
    if hasattr(model, "coef_"):
        values = np.asarray(getattr(model, "coef_"), dtype=float).ravel()
        return pd.DataFrame({"feature": feature_list[: len(values)], "importance": np.abs(values)}).sort_values("importance", ascending=False)
    return pd.DataFrame(columns=["feature", "importance"])


def attach_predictions(df: pd.DataFrame, model: object) -> pd.DataFrame:
    frame = prepare_model_frame(df, feature_list)
    preds = model.predict(frame[feature_list].to_numpy(dtype=float))
    out = df.copy()
    out["predicted_enrolments"] = np.asarray(preds, dtype=float)
    out["residual"] = out["total_enrolments"] - out["predicted_enrolments"]
    out["abs_error"] = out["residual"].abs()
    return out


def page_dashboard(df: pd.DataFrame, model_name: str, model: object) -> None:
    st.title("🪪 Aadhaar Analytics Dashboard")
    st.caption(f"Model-driven dashboard using **{model_name}** for predictions and charts.")

    predicted = attach_predictions(df, model)
    daily = predicted.groupby("date", as_index=False)[["total_enrolments", "predicted_enrolments", "total_demographic_updates", "total_biometric_updates"]].sum()
    state_count = int(predicted["state"].nunique())
    anomaly_count = int(len(anomalies))

    score = None
    if not model_comparison.empty and "Model" in model_comparison.columns:
        match = model_comparison[model_comparison["Model"].astype(str).str.lower() == model_name.lower()]
        if not match.empty:
            score_col = "Test R2" if "Test R2" in match.columns else ("r2" if "r2" in match.columns else None)
            if score_col:
                score = float(match.iloc[0][score_col])

    cols = st.columns(4)
    cols[0].metric("Actual enrolments", f"{int(predicted['total_enrolments'].sum()):,}")
    cols[1].metric("Predicted enrolments", f"{int(predicted['predicted_enrolments'].sum()):,}")
    cols[2].metric("States covered", f"{state_count:,}")
    cols[3].metric("Model R²", f"{score:.3f}" if score is not None else "n/a")

    left, right = st.columns([1.2, 1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["total_enrolments"], name="Actual", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["predicted_enrolments"], name="Predicted", mode="lines"))
        fig.update_layout(height=440, xaxis_title="Date", yaxis_title="Enrolments", title="Actual vs predicted enrolments")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        top_states = (
            predicted.groupby("state", as_index=False)[["total_enrolments", "predicted_enrolments"]]
            .sum()
            .sort_values("predicted_enrolments", ascending=False)
        )
        fig = px.bar(
            top_states,
            x="predicted_enrolments",
            y="state",
            orientation="h",
            color="predicted_enrolments",
            title="States by predicted enrolment",
        )
        fig.update_layout(height=440, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Residuals")
    residual_summary = daily.assign(residual=daily["total_enrolments"] - daily["predicted_enrolments"])
    st.plotly_chart(px.bar(residual_summary, x="date", y="residual", title="Daily residuals"), use_container_width=True)

    st.subheader("Feature importance")
    importance = get_feature_importance(model)
    if importance.empty:
        st.info("This model does not expose feature importance or coefficients.")
    else:
        st.plotly_chart(px.bar(importance.head(15), x="importance", y="feature", orientation="h", title="Top 15 features"), use_container_width=True)

    st.subheader("Age composition")
    age_summary = pd.DataFrame(
        {
            "Age Group": ["0-5", "5-17", "18+"],
            "Count": [predicted["age_0_5"].sum(), predicted["age_5_17"].sum(), predicted["age_18_greater"].sum()],
        }
    )
    st.plotly_chart(px.pie(age_summary, names="Age Group", values="Count", title="Enrolment age distribution"), use_container_width=True)

    st.subheader("Anomalies")
    st.write(f"Flagged rows: {anomaly_count:,}")
    if not anomalies.empty:
        st.dataframe(anomalies[["date", "state", "total_enrolments", "z_score", "severity"]].head(10), use_container_width=True)


def page_trends(df: pd.DataFrame, model_name: str, model: object) -> None:
    st.title("📈 Trends")
    predicted = attach_predictions(df, model)
    ts = predicted.groupby("date", as_index=False)[["total_enrolments", "predicted_enrolments", "total_demographic_updates", "total_biometric_updates"]].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts["date"], y=ts["total_enrolments"], name="Actual", mode="lines"))
    fig.add_trace(go.Scatter(x=ts["date"], y=ts["predicted_enrolments"], name=f"{model_name} prediction", mode="lines"))
    fig.add_trace(go.Scatter(x=ts["date"], y=ts["total_demographic_updates"], name="Demographic updates", mode="lines"))
    fig.add_trace(go.Scatter(x=ts["date"], y=ts["total_biometric_updates"], name="Biometric updates", mode="lines"))
    fig.update_layout(height=520, xaxis_title="Date", yaxis_title="Count", title="Time-series overview")
    st.plotly_chart(fig, use_container_width=True)

    state_ts = predicted.groupby(["date", "state"], as_index=False)[["total_enrolments", "predicted_enrolments"]].sum()
    top_state = state_ts.groupby("state")["total_enrolments"].sum().sort_values(ascending=False).index[0]
    state_line = state_ts[state_ts["state"] == top_state]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=state_line["date"], y=state_line["total_enrolments"], name="Actual"))
    fig.add_trace(go.Scatter(x=state_line["date"], y=state_line["predicted_enrolments"], name="Predicted"))
    fig.update_layout(height=420, title=f"Trend for {top_state}", xaxis_title="Date", yaxis_title="Enrolments")
    st.plotly_chart(fig, use_container_width=True)


def page_geography(df: pd.DataFrame, model_name: str, model: object) -> None:
    st.title("🗺️ Geography")
    st.caption("The model is trained at the state-day level, so this view focuses on state predictions rather than district choropleths.")
    predicted = attach_predictions(df, model)
    state_summary = (
        predicted.groupby("state", as_index=False)[["total_enrolments", "predicted_enrolments"]]
        .sum()
        .sort_values("predicted_enrolments", ascending=False)
    )

    ranking_tab, drilldown_tab, compare_tab = st.tabs(["All states", "Search & drilldown", "Compare states"])

    with ranking_tab:
        st.subheader("All states ranking")
        st.plotly_chart(
            px.bar(state_summary, x="predicted_enrolments", y="state", orientation="h", title="States by predicted enrolment"),
            use_container_width=True,
        )
        with st.expander("Full state table"):
            st.dataframe(state_summary, use_container_width=True)

    with drilldown_tab:
        st.subheader("Search and drill down")
        search_term = st.text_input("Search state", value="").strip().lower()
        searchable_states = state_summary["state"].astype(str)
        if search_term:
            filtered_summary = state_summary[searchable_states.str.lower().str.contains(search_term, na=False)].copy()
        else:
            filtered_summary = state_summary.copy()

        if filtered_summary.empty:
            st.info("No states matched your search.")
        else:
            focused_state = st.selectbox("Focus state", filtered_summary["state"].tolist())
            focus_row = filtered_summary[filtered_summary["state"] == focused_state].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("State", str(focus_row["state"]))
            c2.metric("Actual enrolments", f"{int(focus_row['total_enrolments']):,}")
            c3.metric("Predicted enrolments", f"{int(focus_row['predicted_enrolments']):,}")

            history = predicted[predicted["state"] == focused_state].sort_values("date")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=history["date"], y=history["total_enrolments"], name="Actual"))
            fig.add_trace(go.Scatter(x=history["date"], y=history["predicted_enrolments"], name="Predicted"))
            fig.update_layout(height=360, title=f"Trend for {focused_state}", xaxis_title="Date", yaxis_title="Enrolments")
            st.plotly_chart(fig, use_container_width=True)

    with compare_tab:
        st.subheader("Compare two states")
        compare_states = state_summary["state"].tolist()
        left_state = st.selectbox("First state", compare_states, index=0, key="geo_compare_left")
        right_state = st.selectbox("Second state", compare_states, index=min(1, len(compare_states) - 1), key="geo_compare_right")

        compare_frame = state_summary[state_summary["state"].isin([left_state, right_state])].copy()
        st.plotly_chart(
            px.bar(compare_frame, x="state", y="predicted_enrolments", color="state", title="Predicted enrolments comparison"),
            use_container_width=True,
        )
        st.dataframe(compare_frame, use_container_width=True)


def page_anomalies(df: pd.DataFrame, model_name: str, model: object) -> None:
    st.title("🚨 Anomalies")
    predicted = attach_predictions(df, model)
    states = sorted(predicted["state"].dropna().unique().tolist())
    selected_states = st.multiselect("Filter states", states, default=states)
    view = predicted.copy()
    if selected_states:
        view = view[view["state"].isin(selected_states)]
    view = view.sort_values("abs_error", ascending=False)
    st.dataframe(view[["date", "state", "total_enrolments", "predicted_enrolments", "residual", "abs_error"]].head(25), use_container_width=True)

    if not view.empty:
        selected_state = st.selectbox("State for context chart", sorted(view["state"].dropna().unique().tolist()))
        history = view[view["state"] == selected_state].sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=history["date"], y=history["total_enrolments"], name="Actual"))
        fig.add_trace(go.Scatter(x=history["date"], y=history["predicted_enrolments"], name="Predicted"))
        fig.update_layout(height=420, title=f"Model context — {selected_state}", xaxis_title="Date", yaxis_title="Enrolments")
        st.plotly_chart(fig, use_container_width=True)


def page_forecast(df: pd.DataFrame, model_name: str, model: object) -> None:
    st.title("🔮 Forecast")
    states = sorted(df["state"].dropna().unique().tolist())
    state = st.selectbox("State", states)
    horizon = st.select_slider("Forecast horizon", options=[30, 60, 90], value=90)
    forecast_df = recursive_forecast_lightgbm(model, df, horizon, state, feature_list, None)
    history = df[df["state"] == state].sort_values("date").tail(180)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["date"], y=history["total_enrolments"], name="History"))
    fig.add_trace(go.Scatter(x=forecast_df["date"], y=forecast_df["forecast"], name=f"{model_name} forecast"))
    fig.update_layout(height=520, xaxis_title="Date", yaxis_title="Enrolments")
    st.plotly_chart(fig, use_container_width=True)
    st.download_button(
        "Download forecast CSV",
        forecast_df.to_csv(index=False).encode("utf-8"),
        file_name=f"forecast_{state}_{horizon}.csv",
        mime="text/csv",
    )


def page_model_report(model_name: str, model: object) -> None:
    st.title("📋 Model Report")
    metrics = pd.DataFrame(model_comparison)
    if metrics.empty:
        st.info("No comparison metrics were found in `models/model_comparison.json`.")
    else:
        st.dataframe(metrics, use_container_width=True)
        metric_col = "Test R2" if "Test R2" in metrics.columns else ("r2" if "r2" in metrics.columns else metrics.columns[1])
        st.plotly_chart(px.bar(metrics, x="Model", y=metric_col, title="Model comparison"), use_container_width=True)

    importance = get_feature_importance(model)
    if not importance.empty:
        st.plotly_chart(px.bar(importance.head(15), x="importance", y="feature", orientation="h", title=f"Top features for {model_name}"), use_container_width=True)

    if st.button("Generate EDA exports"):
        paths = generate_eda_artifacts(panel)
        st.success(f"Generated {len(paths)} chart files in outputs/")


filtered_panel = sidebar_filters(panel)
selected_model_name, selected_model = selected_model_sidebar()
page = st.sidebar.radio("Navigate", ["Dashboard", "Trends", "Geography", "Anomalies", "Forecast", "Model Report"])

if selected_model is None:
    st.error("No compatible model could be loaded from the saved artifacts.")
elif page == "Dashboard":
    page_dashboard(filtered_panel, selected_model_name, selected_model)
elif page == "Trends":
    page_trends(filtered_panel, selected_model_name, selected_model)
elif page == "Geography":
    page_geography(filtered_panel, selected_model_name, selected_model)
elif page == "Anomalies":
    page_anomalies(filtered_panel, selected_model_name, selected_model)
elif page == "Forecast":
    page_forecast(filtered_panel, selected_model_name, selected_model)
else:
    page_model_report(selected_model_name, selected_model)
