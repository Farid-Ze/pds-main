"""Visualisasi COVID-19.

Menampilkan berbagai chart untuk analisis trend:
- Line Chart: Trend kasus, kematian, recovery
- Bar Chart: Daily new cases
- Area Chart: Kumulatif stacked
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

import utils
import ui


def tampilkan_visualisasi_covid(df: pd.DataFrame):
    """Tampilkan halaman visualisasi COVID-19."""
    
    st.title("Visualisasi COVID-19")
    st.markdown("Analisis visual trend COVID-19 Indonesia dari waktu ke waktu.")
    
    if df.empty:
        st.warning("Data tidak tersedia. Silakan coba lagi nanti.")
        return
    
    st.divider()
    
    # --- Filter Section ---
    st.subheader("Filter Data")
    
    col1, col2 = st.columns(2)
    
    min_date = df["Tanggal"].min().date()
    max_date = df["Tanggal"].max().date()
    
    with col1:
        start_date = st.date_input(
            "Tanggal Mulai",
            value=max_date - timedelta(days=365),
            min_value=min_date,
            max_value=max_date,
            key="viz_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "Tanggal Akhir",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="viz_end_date"
        )
    
    # Filter data
    df_filtered = utils.filter_by_date_range(df, start_date, end_date)
    
    if df_filtered.empty:
        st.warning("Tidak ada data untuk rentang tanggal yang dipilih.")
        return
    
    st.caption(f"Menampilkan {len(df_filtered):,} hari data")
    
    st.divider()
    
    # --- Tab Navigation ---
    tab_selected = ui.section_nav(
        "Jenis Visualisasi",
        options=["Trend Kumulatif", "Kasus Harian", "Perbandingan", "Distribusi"],
        key="viz_tab",
    )
    
    st.divider()
    
    if tab_selected == "Trend Kumulatif":
        _show_cumulative_trend(df_filtered)
    
    elif tab_selected == "Kasus Harian":
        _show_daily_cases(df_filtered)
    
    elif tab_selected == "Perbandingan":
        _show_comparison(df_filtered)
    
    elif tab_selected == "Distribusi":
        _show_distribution(df_filtered)


def _show_cumulative_trend(df: pd.DataFrame):
    """Tampilkan trend kumulatif."""
    
    st.subheader("Trend Kumulatif COVID-19")
    
    # Pilih metrik
    metrics = st.multiselect(
        "Pilih Metrik",
        options=["Kasus", "Kematian", "Sembuh"],
        default=["Kasus", "Kematian"],
        key="viz_cumulative_metrics"
    )
    
    if not metrics:
        st.info("Pilih minimal satu metrik untuk ditampilkan.")
        return
    
    fig = go.Figure()
    
    colors = {
        "Kasus": "rgba(124, 58, 237, 0.8)",
        "Kematian": "rgba(220, 38, 38, 0.8)",
        "Sembuh": "rgba(34, 197, 94, 0.8)",
    }
    
    for metric in metrics:
        if metric in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Tanggal"],
                y=df[metric],
                name=metric,
                mode="lines",
                line=dict(color=colors.get(metric, "gray"), width=2),
                fill="tonexty" if metric == "Sembuh" else None,
            ))
    
    fig.update_layout(
        title="Trend Kumulatif COVID-19 Indonesia",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah",
        hovermode="x unified",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    st.plotly_chart(fig, **ui.kw_plotly_chart())


def _show_daily_cases(df: pd.DataFrame):
    """Tampilkan kasus harian."""
    
    st.subheader("Kasus Baru Harian")
    
    # Pilih metrik
    metric = st.radio(
        "Pilih Metrik",
        options=["Kasus_Baru", "Kematian_Baru"],
        format_func=lambda x: "Kasus Baru" if x == "Kasus_Baru" else "Kematian Baru",
        horizontal=True,
        key="viz_daily_metric"
    )
    
    # Rolling average toggle
    show_rolling = st.checkbox("Tampilkan Rata-rata 7 Hari", value=True, key="viz_show_rolling")
    
    fig = go.Figure()
    
    color = "rgba(124, 58, 237, 0.6)" if metric == "Kasus_Baru" else "rgba(220, 38, 38, 0.6)"
    
    fig.add_trace(go.Bar(
        x=df["Tanggal"],
        y=df[metric],
        name="Harian",
        marker_color=color,
    ))
    
    if show_rolling:
        rolling = df[metric].rolling(window=7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["Tanggal"],
            y=rolling,
            name="Rata-rata 7 Hari",
            line=dict(color="rgba(0, 0, 0, 0.8)", width=2),
        ))
    
    title = "Kasus Baru Harian" if metric == "Kasus_Baru" else "Kematian Baru Harian"
    
    fig.update_layout(
        title=title,
        xaxis_title="Tanggal",
        yaxis_title="Jumlah",
        hovermode="x unified",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    st.plotly_chart(fig, **ui.kw_plotly_chart())


def _show_comparison(df: pd.DataFrame):
    """Tampilkan perbandingan metrik."""
    
    st.subheader("Perbandingan Kasus vs Kematian vs Sembuh")
    
    # Normalisasi untuk perbandingan
    df_norm = df.copy()
    
    fig = go.Figure()
    
    # Area chart stacked
    fig.add_trace(go.Scatter(
        x=df_norm["Tanggal"],
        y=df_norm["Kematian"],
        name="Kematian",
        stackgroup="one",
        fillcolor="rgba(220, 38, 38, 0.7)",
        line=dict(width=0),
    ))
    
    fig.add_trace(go.Scatter(
        x=df_norm["Tanggal"],
        y=df_norm["Sembuh"],
        name="Sembuh",
        stackgroup="one",
        fillcolor="rgba(34, 197, 94, 0.7)",
        line=dict(width=0),
    ))
    
    # Kasus total sebagai line
    fig.add_trace(go.Scatter(
        x=df_norm["Tanggal"],
        y=df_norm["Kasus"],
        name="Total Kasus",
        mode="lines",
        line=dict(color="rgba(124, 58, 237, 1)", width=2),
    ))
    
    fig.update_layout(
        title="Perbandingan Jumlah Kasus, Sembuh, dan Kematian",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah",
        hovermode="x unified",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    st.plotly_chart(fig, **ui.kw_plotly_chart())


def _show_distribution(df: pd.DataFrame):
    """Tampilkan distribusi kasus."""
    
    st.subheader("Distribusi Kasus Baru Harian")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig_hist = px.histogram(
            df,
            x="Kasus_Baru",
            nbins=50,
            title="Histogram Kasus Baru Harian",
            labels={"Kasus_Baru": "Kasus Baru", "count": "Frekuensi"},
            color_discrete_sequence=["rgba(124, 58, 237, 0.7)"],
        )
        fig_hist.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_hist, **ui.kw_plotly_chart())
    
    with col2:
        # Box plot per bulan
        df_with_month = utils.add_date_features(df)
        
        fig_box = px.box(
            df_with_month,
            x="Bulan",
            y="Kasus_Baru",
            title="Distribusi Kasus Baru per Bulan",
            labels={"Kasus_Baru": "Kasus Baru", "Bulan": "Bulan"},
            color_discrete_sequence=["rgba(124, 58, 237, 0.7)"],
        )
        fig_box.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_box, **ui.kw_plotly_chart())
