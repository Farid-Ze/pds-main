"""Trend Vaksinasi COVID-19.

Menampilkan data dan trend vaksinasi:
- Total vaksinasi
- Dosis harian
- Persentase populasi tervaksinasi
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import utils
import ui
import api_client


@st.cache_data(ttl=60 * 60, show_spinner=False)
def _load_vaccine_data():
    """Load data vaksinasi dengan cache."""
    return api_client.get_vaccine_df()


def tampilkan_trend_vaksinasi():
    """Tampilkan halaman trend vaksinasi."""
    
    st.title("Trend Vaksinasi COVID-19")
    st.markdown("Analisis data vaksinasi COVID-19 Indonesia.")
    
    # Load vaccine data
    with st.spinner("Memuat data vaksinasi..."):
        df = _load_vaccine_data()
    
    if df.empty:
        st.warning("Data vaksinasi tidak tersedia.")
        return
    
    # Info tentang data
    ui.info_callout(
        "Data vaksinasi diambil dari API atau menggunakan data simulasi jika tidak tersedia.",
        icon="ℹ️"
    )
    
    st.divider()
    
    # --- Statistik Ringkasan ---
    st.subheader("Statistik Vaksinasi")
    
    total_vaccinated = df["Total_Vaksin"].max()
    population = 279_134_505  # Populasi Indonesia
    percentage = (total_vaccinated / population) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Dosis",
            value=utils.format_number(total_vaccinated),
            help="Total dosis vaksin yang telah diberikan"
        )
    
    with col2:
        st.metric(
            label="Persentase Populasi",
            value=utils.format_percentage(percentage),
            help="Persentase terhadap total populasi (dosis)"
        )
    
    with col3:
        # Rata-rata dosis harian
        avg_daily = df["Dosis_Harian"].mean()
        st.metric(
            label="Rata-rata Dosis/Hari",
            value=utils.format_number(avg_daily),
            help="Rata-rata dosis harian"
        )
    
    with col4:
        # Peak vaksinasi
        max_daily = df["Dosis_Harian"].max()
        st.metric(
            label="Dosis Tertinggi/Hari",
            value=utils.format_number(max_daily),
            help="Dosis tertinggi dalam satu hari"
        )
    
    st.divider()
    
    # --- Trend Chart ---
    st.subheader("Trend Vaksinasi")
    
    tab_selected = ui.section_nav(
        "Tampilan",
        options=["Kumulatif", "Harian"],
        key="vaccine_tab",
    )
    
    if tab_selected == "Kumulatif":
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["Tanggal"],
            y=df["Total_Vaksin"],
            name="Total Dosis",
            mode="lines",
            fill="tozeroy",
            line=dict(color="rgba(34, 197, 94, 0.8)", width=2),
            fillcolor="rgba(34, 197, 94, 0.3)",
        ))
        
        fig.update_layout(
            title="Total Dosis Vaksin Kumulatif",
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Dosis",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0),
        )
        
        st.plotly_chart(fig, **ui.kw_plotly_chart())
    
    else:  # Harian
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df["Tanggal"],
            y=df["Dosis_Harian"],
            name="Dosis Harian",
            marker_color="rgba(34, 197, 94, 0.6)",
        ))
        
        # Rolling average
        rolling = df["Dosis_Harian"].rolling(window=7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["Tanggal"],
            y=rolling,
            name="Rata-rata 7 Hari",
            line=dict(color="rgba(0, 0, 0, 0.8)", width=2),
        ))
        
        fig.update_layout(
            title="Dosis Vaksin Harian",
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Dosis",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        
        st.plotly_chart(fig, **ui.kw_plotly_chart())
    
    st.divider()
    
    # --- Progress Bars ---
    st.subheader("Progress Vaksinasi")
    
    # Simulasi progress untuk dosis berbeda
    # Dalam realita, ini akan dari API
    dosis_1_pct = min(percentage * 0.85, 80)  # Simulasi dosis 1
    dosis_2_pct = min(percentage * 0.70, 70)  # Simulasi dosis 2
    booster_pct = min(percentage * 0.30, 30)  # Simulasi booster
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Dosis 1**")
        st.progress(dosis_1_pct / 100, text=f"{dosis_1_pct:.1f}%")
    
    with col2:
        st.markdown("**Dosis 2**")
        st.progress(dosis_2_pct / 100, text=f"{dosis_2_pct:.1f}%")
    
    with col3:
        st.markdown("**Booster**")
        st.progress(booster_pct / 100, text=f"{booster_pct:.1f}%")
    
    st.caption("Persentase dari total populasi Indonesia (~279 juta jiwa)")
    
    st.divider()
    
    # --- Monthly Summary ---
    st.subheader("Ringkasan Bulanan")
    
    df_monthly = df.copy()
    df_monthly["Bulan"] = df_monthly["Tanggal"].dt.to_period("M")
    monthly_summary = df_monthly.groupby("Bulan").agg({
        "Dosis_Harian": ["sum", "mean", "max"]
    }).reset_index()
    monthly_summary.columns = ["Bulan", "Total Dosis", "Rata-rata/Hari", "Maks/Hari"]
    monthly_summary["Bulan"] = monthly_summary["Bulan"].astype(str)
    
    # Show last 12 months
    monthly_summary = monthly_summary.tail(12)
    
    # Format numbers
    for col in ["Total Dosis", "Rata-rata/Hari", "Maks/Hari"]:
        monthly_summary[col] = monthly_summary[col].apply(lambda x: utils.format_number(x))
    
    st.dataframe(monthly_summary, use_container_width=True, hide_index=True)
