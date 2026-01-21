"""Statistik Data COVID-19.

Menampilkan analisis statistik lengkap:
- CFR, Recovery Rate
- Peak analysis
- Rolling averages
- Histogram dan box plot
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import utils
import ui


def tampilkan_statistik_data(df: pd.DataFrame, current_stats: dict):
    """Tampilkan halaman statistik data."""
    
    st.title("Statistik Data COVID-19")
    st.markdown("Analisis statistik lengkap data COVID-19 Indonesia.")
    
    if df.empty:
        st.warning("Data tidak tersedia.")
        return
    
    st.divider()
    
    # --- Statistik Ringkasan ---
    st.subheader("Statistik Ringkasan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    cases = current_stats.get("cases", 0)
    deaths = current_stats.get("deaths", 0)
    recovered = current_stats.get("recovered", 0)
    
    cfr = utils.calculate_cfr(deaths, cases)
    recovery_rate = utils.calculate_recovery_rate(recovered, cases)
    
    with col1:
        st.metric(
            label="Case Fatality Rate (CFR)",
            value=utils.format_percentage(cfr),
            help="(Total Kematian / Total Kasus) × 100"
        )
    
    with col2:
        st.metric(
            label="Recovery Rate",
            value=utils.format_percentage(recovery_rate),
            help="(Total Sembuh / Total Kasus) × 100"
        )
    
    with col3:
        # R0 estimate
        r0 = utils.calculate_r0_estimate(df)
        st.metric(
            label="Estimasi R0 (terkini)",
            value=f"{r0:.2f}",
            help="Estimasi reproduction number berdasarkan trend kasus"
        )
    
    with col4:
        # Trend direction
        trend = utils.get_trend_direction(df, "Kasus_Baru")
        trend_icon = utils.get_trend_icon(trend)
        st.metric(
            label="Trend Kasus",
            value=f"{trend_icon} {trend.title()}",
            help="Arah trend kasus dalam 14 hari terakhir"
        )
    
    st.divider()
    
    # --- Peak Analysis ---
    st.subheader("Analisis Puncak (Peak)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        peak_cases = utils.get_peak_info(df, "Kasus_Baru")
        st.markdown("### Puncak Kasus Baru")
        if peak_cases["date"]:
            st.markdown(f"**Tanggal:** {peak_cases['date'].strftime('%d %B %Y')}")
            st.markdown(f"**Jumlah:** {utils.format_number(peak_cases['value'])} kasus")
    
    with col2:
        peak_deaths = utils.get_peak_info(df, "Kematian_Baru")
        st.markdown("### Puncak Kematian Baru")
        if peak_deaths["date"]:
            st.markdown(f"**Tanggal:** {peak_deaths['date'].strftime('%d %B %Y')}")
            st.markdown(f"**Jumlah:** {utils.format_number(peak_deaths['value'])} kematian")
    
    st.divider()
    
    # --- Statistik Deskriptif ---
    st.subheader("Statistik Deskriptif - Kasus Baru Harian")
    
    stats = utils.calculate_statistics(df, "Kasus_Baru")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rata-rata", utils.format_number(stats.get("mean", 0)))
            st.metric("Median", utils.format_number(stats.get("median", 0)))
        
        with col2:
            st.metric("Std Deviasi", utils.format_number(stats.get("std", 0)))
            st.metric("Total Data", utils.format_number(stats.get("count", 0)))
        
        with col3:
            st.metric("Minimum", utils.format_number(stats.get("min", 0)))
            st.metric("Q1 (25%)", utils.format_number(stats.get("q1", 0)))
        
        with col4:
            st.metric("Maximum", utils.format_number(stats.get("max", 0)))
            st.metric("Q3 (75%)", utils.format_number(stats.get("q3", 0)))
    
    st.divider()
    
    # --- Charts ---
    st.subheader("Visualisasi Statistik")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig_hist = px.histogram(
            df,
            x="Kasus_Baru",
            nbins=50,
            title="Distribusi Kasus Baru Harian",
            labels={"Kasus_Baru": "Kasus Baru", "count": "Frekuensi"},
            color_discrete_sequence=["rgba(124, 58, 237, 0.7)"],
        )
        fig_hist.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_hist, **ui.kw_plotly_chart())
    
    with col2:
        # Box plot
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=df["Kasus_Baru"],
            name="Kasus Baru",
            marker_color="rgba(124, 58, 237, 0.7)",
        ))
        fig_box.update_layout(
            title="Box Plot Kasus Baru Harian",
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_box, **ui.kw_plotly_chart())
    
    st.divider()
    
    # --- Rolling Average Chart ---
    st.subheader("Rata-rata Bergerak (Rolling Average)")
    
    window = st.slider(
        "Ukuran Window (hari)",
        min_value=3,
        max_value=30,
        value=7,
        key="stats_rolling_window"
    )
    
    df_rolling = df.copy()
    df_rolling["Rolling"] = utils.calculate_rolling_average(df, "Kasus_Baru", window)
    
    fig_rolling = go.Figure()
    
    fig_rolling.add_trace(go.Scatter(
        x=df_rolling["Tanggal"],
        y=df_rolling["Kasus_Baru"],
        name="Kasus Baru",
        mode="lines",
        line=dict(color="rgba(124, 58, 237, 0.3)", width=1),
    ))
    
    fig_rolling.add_trace(go.Scatter(
        x=df_rolling["Tanggal"],
        y=df_rolling["Rolling"],
        name=f"Rata-rata {window} Hari",
        mode="lines",
        line=dict(color="rgba(124, 58, 237, 1)", width=2),
    ))
    
    fig_rolling.update_layout(
        title=f"Kasus Baru dengan Rata-rata {window} Hari",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah Kasus",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    st.plotly_chart(fig_rolling, **ui.kw_plotly_chart())
