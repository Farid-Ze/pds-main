"""Kalkulator Risiko COVID-19.

Menyediakan kalkulator interaktif untuk:
- Case Fatality Rate (CFR)
- Basic Reproduction Number (R0)
- Herd Immunity Threshold
"""

import streamlit as st
import plotly.graph_objects as go

import utils
import ui


def tampilkan_kalkulator_risiko(current_stats: dict):
    """Tampilkan halaman kalkulator risiko."""
    
    st.title("Kalkulator Risiko COVID-19")
    st.markdown("Kalkulator interaktif untuk analisis epidemiologi COVID-19.")
    
    st.divider()
    
    # --- Tab Navigation ---
    tab_selected = ui.section_nav(
        "Jenis Kalkulator",
        options=["CFR Calculator", "R0 & Herd Immunity", "Proyeksi Kasus"],
        key="calc_tab",
    )
    
    st.divider()
    
    if tab_selected == "CFR Calculator":
        _show_cfr_calculator(current_stats)
    
    elif tab_selected == "R0 & Herd Immunity":
        _show_r0_calculator()
    
    elif tab_selected == "Proyeksi Kasus":
        _show_projection_calculator()


def _show_cfr_calculator(current_stats: dict):
    """Tampilkan kalkulator CFR."""
    
    st.subheader("Kalkulator Case Fatality Rate (CFR)")
    
    st.markdown("""
    **Case Fatality Rate (CFR)** adalah persentase kasus yang berakhir dengan kematian.
    
    Formula: `CFR = (Total Kematian / Total Kasus) × 100`
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Input Manual")
        
        cases = st.number_input(
            "Total Kasus",
            min_value=0,
            value=current_stats.get("cases", 0),
            step=1000,
            key="cfr_cases"
        )
        
        deaths = st.number_input(
            "Total Kematian",
            min_value=0,
            value=current_stats.get("deaths", 0),
            step=100,
            key="cfr_deaths"
        )
        
        if ui.button("Hitung CFR", key="calc_cfr"):
            cfr = utils.calculate_cfr(deaths, cases)
            st.session_state["cfr_result"] = cfr
    
    with col2:
        st.markdown("### Hasil")
        
        if "cfr_result" in st.session_state:
            cfr = st.session_state["cfr_result"]
            
            st.metric(
                label="Case Fatality Rate",
                value=utils.format_percentage(cfr),
            )
            
            # Interpretation
            if cfr < 1:
                st.success("CFR rendah (< 1%): Angka kematian relatif rendah.")
            elif cfr < 3:
                st.warning("CFR sedang (1-3%): Perlu kewaspadaan.")
            else:
                st.error("CFR tinggi (> 3%): Angka kematian signifikan.")
            
            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=cfr,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "CFR (%)"},
                gauge={
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "rgba(124, 58, 237, 0.8)"},
                    'steps': [
                        {'range': [0, 1], 'color': "rgba(34, 197, 94, 0.3)"},
                        {'range': [1, 3], 'color': "rgba(234, 179, 8, 0.3)"},
                        {'range': [3, 10], 'color': "rgba(220, 38, 38, 0.3)"},
                    ],
                },
            ))
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, **ui.kw_plotly_chart())
    
    st.divider()
    
    # CFR Indonesia actual
    st.markdown("### CFR Indonesia (Data Aktual)")
    
    actual_cfr = utils.calculate_cfr(
        current_stats.get("deaths", 0),
        current_stats.get("cases", 0)
    )
    
    st.info(f"CFR Indonesia saat ini: **{utils.format_percentage(actual_cfr)}**")


def _show_r0_calculator():
    """Tampilkan kalkulator R0 dan Herd Immunity."""
    
    st.subheader("Kalkulator R0 & Herd Immunity")
    
    st.markdown("""
    **R0 (Basic Reproduction Number)** adalah rata-rata jumlah orang yang terinfeksi 
    dari satu orang yang terinfeksi dalam populasi yang rentan.
    
    **Herd Immunity Threshold** adalah persentase populasi yang perlu kebal untuk 
    menghentikan penyebaran penyakit.
    
    Formula: `Herd Immunity Threshold = 1 - (1/R0)`
    """)
    
    # Handle preset buttons BEFORE slider to avoid session_state conflict
    # Check if any preset was clicked (we use a temporary key)
    if "r0_input" not in st.session_state:
        st.session_state["r0_input"] = 2.5
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Input R0")
        
        # Quick presets - rendered before slider, but we handle clicks via callback
        st.markdown("**Preset Varian:**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Asli (2.5)", key="preset_original"):
                st.session_state["r0_input"] = 2.5
                st.rerun()
        with col_b:
            if st.button("Delta (6)", key="preset_delta"):
                st.session_state["r0_input"] = 6.0
                st.rerun()
        with col_c:
            if st.button("Omicron (10)", key="preset_omicron"):
                st.session_state["r0_input"] = 10.0
                st.rerun()
        
        r0 = st.slider(
            "Nilai R0",
            min_value=0.5,
            max_value=10.0,
            step=0.1,
            key="r0_input",
            help="COVID-19 asli: ~2.5, Delta: ~5-8, Omicron: ~8-15"
        )
    
    with col2:
        st.markdown("### Hasil")
        
        herd_threshold = utils.calculate_herd_immunity_threshold(r0)
        
        col_x, col_y = st.columns(2)
        
        with col_x:
            st.metric(
                label="R0",
                value=f"{r0:.1f}",
                help="Basic Reproduction Number"
            )
        
        with col_y:
            st.metric(
                label="Herd Immunity Threshold",
                value=utils.format_percentage(herd_threshold),
                help="Persentase populasi yang perlu kebal"
            )
        
        # Visualization
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=herd_threshold,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Herd Immunity Threshold (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "rgba(124, 58, 237, 0.8)"},
                'steps': [
                    {'range': [0, 50], 'color': "rgba(34, 197, 94, 0.3)"},
                    {'range': [50, 80], 'color': "rgba(234, 179, 8, 0.3)"},
                    {'range': [80, 100], 'color': "rgba(220, 38, 38, 0.3)"},
                ],
            },
        ))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, **ui.kw_plotly_chart())
    
    st.divider()
    
    # Interpretation
    st.markdown("### Interpretasi")
    
    if r0 < 1:
        st.success(f"R0 = {r0:.1f}: Penyakit akan mati sendiri tanpa perlu herd immunity.")
    elif herd_threshold < 50:
        st.success(f"Dengan R0 = {r0:.1f}, herd immunity dapat dicapai dengan vaksinasi ~{herd_threshold:.0f}% populasi.")
    elif herd_threshold < 80:
        st.warning(f"Dengan R0 = {r0:.1f}, dibutuhkan vaksinasi ~{herd_threshold:.0f}% populasi. Ini menantang tapi mungkin.")
    else:
        st.error(f"Dengan R0 = {r0:.1f}, herd immunity membutuhkan ~{herd_threshold:.0f}% populasi kebal. Ini sangat sulit dicapai.")


def _show_projection_calculator():
    """Tampilkan proyeksi kasus sederhana."""
    
    st.subheader("Proyeksi Kasus Sederhana")
    
    st.markdown("""
    Proyeksi pertumbuhan kasus berdasarkan pertumbuhan eksponensial sederhana.
    
    Formula: `Kasus(t) = Kasus_awal × (1 + growth_rate)^t`
    
    ⚠️ **Catatan**: Proyeksi ini sangat sederhana dan tidak memperhitungkan faktor-faktor 
    kompleks seperti intervensi, herd immunity, perubahan perilaku, dll.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Parameter")
        
        initial_cases = st.number_input(
            "Kasus Awal (per hari)",
            min_value=1,
            value=1000,
            step=100,
            key="proj_initial"
        )
        
        growth_rate = st.slider(
            "Tingkat Pertumbuhan (%/hari)",
            min_value=-20.0,
            max_value=50.0,
            value=5.0,
            step=0.5,
            key="proj_growth"
        )
        
        days = st.slider(
            "Proyeksi (hari)",
            min_value=7,
            max_value=90,
            value=30,
            step=7,
            key="proj_days"
        )
    
    with col2:
        st.markdown("### Hasil Proyeksi")
        
        # Calculate projection
        import numpy as np
        
        t = np.arange(days + 1)
        cases = initial_cases * ((1 + growth_rate / 100) ** t)
        
        final_cases = cases[-1]
        total_new = sum(cases)
        
        st.metric(
            label=f"Kasus/Hari (Hari ke-{days})",
            value=utils.format_number(final_cases),
        )
        
        st.metric(
            label="Total Kasus Baru (periode)",
            value=utils.format_number(total_new),
        )
        
        # Doubling time
        if growth_rate > 0:
            doubling = np.log(2) / np.log(1 + growth_rate / 100)
            st.metric(
                label="Waktu Penggandaan",
                value=f"{doubling:.1f} hari",
            )
    
    st.divider()
    
    # Chart
    st.markdown("### Grafik Proyeksi")
    
    import pandas as pd
    
    df_proj = pd.DataFrame({
        "Hari": t,
        "Kasus": cases,
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_proj["Hari"],
        y=df_proj["Kasus"],
        mode="lines+markers",
        name="Proyeksi Kasus",
        line=dict(color="rgba(124, 58, 237, 0.8)", width=2),
    ))
    
    fig.update_layout(
        title=f"Proyeksi Kasus ({days} Hari)",
        xaxis_title="Hari",
        yaxis_title="Kasus per Hari",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    st.plotly_chart(fig, **ui.kw_plotly_chart())
