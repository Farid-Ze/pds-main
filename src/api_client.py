"""API Client untuk COVID-19 Dashboard.

Tujuan file ini:
- Menyediakan fungsi fetch data dari disease.sh API
- Menyediakan data simulasi per provinsi untuk GIS
- Error handling dengan fallback ke sample data
"""

from __future__ import annotations

import os
from typing import Optional
from datetime import datetime

import requests
import pandas as pd


def _get_config_value(key: str, default: str = "") -> str:
    """Ambil konfigurasi dari environment variable."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    
    value = os.getenv(key)
    return str(value).strip() if value else default


def _get_base_url() -> str:
    """Get API base URL."""
    return _get_config_value("COVID_API_BASE_URL", "https://disease.sh/v3/covid-19")


def fetch_indonesia_current() -> Optional[dict]:
    """
    Fetch data COVID-19 Indonesia terkini.
    
    Returns:
        dict dengan keys: cases, deaths, recovered, active, critical, dll.
    """
    try:
        url = f"{_get_base_url()}/countries/indonesia"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching current data: {e}")
        return None


def fetch_indonesia_historical(last_days: str = "all") -> Optional[dict]:
    """
    Fetch data historis COVID-19 Indonesia.
    
    Args:
        last_days: Jumlah hari terakhir atau "all" untuk semua data
        
    Returns:
        dict dengan timeline cases, deaths, recovered
    """
    try:
        url = f"{_get_base_url()}/historical/indonesia?lastdays={last_days}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


def fetch_vaccine_data() -> Optional[dict]:
    """
    Fetch data vaksinasi Indonesia.
    
    Returns:
        dict dengan data vaksinasi atau None jika tidak tersedia
    """
    try:
        url = f"{_get_base_url()}/vaccine/coverage/countries/indonesia?lastdays=all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching vaccine data: {e}")
        return None


def get_historical_df() -> pd.DataFrame:
    """
    Fetch dan konversi data historis ke DataFrame.
    
    Returns:
        DataFrame dengan kolom: Tanggal, Kasus, Kematian, Sembuh, Kasus_Baru, Kematian_Baru
    """
    data = fetch_indonesia_historical()
    
    if data is None or "timeline" not in data:
        return _get_sample_historical_df()
    
    timeline = data["timeline"]
    
    # Parse timeline
    rows = []
    dates = list(timeline.get("cases", {}).keys())
    
    for date_str in dates:
        try:
            # Format: "1/22/20" -> datetime
            dt = datetime.strptime(date_str, "%m/%d/%y")
            cases = timeline.get("cases", {}).get(date_str, 0)
            deaths = timeline.get("deaths", {}).get(date_str, 0)
            recovered = timeline.get("recovered", {}).get(date_str, 0)
            
            rows.append({
                "Tanggal": dt,
                "Kasus": cases,
                "Kematian": deaths,
                "Sembuh": recovered,
            })
        except Exception:
            continue
    
    if not rows:
        return _get_sample_historical_df()
    
    df = pd.DataFrame(rows)
    df = df.sort_values("Tanggal").reset_index(drop=True)
    
    # Hitung daily new cases (delta dari hari sebelumnya)
    df["Kasus_Baru"] = df["Kasus"].diff().fillna(0).clip(lower=0).astype(int)
    df["Kematian_Baru"] = df["Kematian"].diff().fillna(0).clip(lower=0).astype(int)
    df["Sembuh_Baru"] = df["Sembuh"].diff().fillna(0).clip(lower=0).astype(int)
    
    return df


def _get_sample_historical_df() -> pd.DataFrame:
    """
    Fallback: DataFrame sample jika API gagal.
    """
    import numpy as np
    
    # Generate sample data untuk 365 hari
    dates = pd.date_range(start="2020-03-01", periods=365, freq="D")
    
    np.random.seed(42)
    
    # Simulasi kurva pandemi
    days = np.arange(365)
    base_curve = 100 * np.exp(-((days - 150) ** 2) / 5000)
    noise = np.random.normal(0, 10, 365)
    daily_cases = (base_curve + noise).clip(min=1).astype(int)
    
    cumulative_cases = np.cumsum(daily_cases)
    cumulative_deaths = (cumulative_cases * 0.025).astype(int)
    cumulative_recovered = (cumulative_cases * 0.85).astype(int)
    
    df = pd.DataFrame({
        "Tanggal": dates,
        "Kasus": cumulative_cases,
        "Kematian": cumulative_deaths,
        "Sembuh": cumulative_recovered,
        "Kasus_Baru": daily_cases,
        "Kematian_Baru": (daily_cases * 0.025).astype(int),
        "Sembuh_Baru": (daily_cases * 0.85).astype(int),
    })
    
    return df


# Data koordinat provinsi Indonesia
PROVINSI_COORDS = {
    "Aceh": {"lat": 4.695135, "lon": 96.749397},
    "Sumatera Utara": {"lat": 2.115355, "lon": 99.545097},
    "Sumatera Barat": {"lat": -0.739940, "lon": 100.800000},
    "Riau": {"lat": 1.598780, "lon": 101.245830},
    "Jambi": {"lat": -1.589980, "lon": 103.620000},
    "Sumatera Selatan": {"lat": -3.319440, "lon": 104.914440},
    "Bengkulu": {"lat": -3.800000, "lon": 102.266670},
    "Lampung": {"lat": -4.558580, "lon": 105.406670},
    "Kep. Bangka Belitung": {"lat": -2.741050, "lon": 106.440580},
    "Kep. Riau": {"lat": 3.945640, "lon": 108.142860},
    "DKI Jakarta": {"lat": -6.211544, "lon": 106.845172},
    "Jawa Barat": {"lat": -7.090911, "lon": 107.668887},
    "Jawa Tengah": {"lat": -7.150975, "lon": 110.140259},
    "DI Yogyakarta": {"lat": -7.797068, "lon": 110.370529},
    "Jawa Timur": {"lat": -7.536064, "lon": 112.238402},
    "Banten": {"lat": -6.405817, "lon": 106.064018},
    "Bali": {"lat": -8.340930, "lon": 115.091950},
    "Nusa Tenggara Barat": {"lat": -8.652930, "lon": 117.361640},
    "Nusa Tenggara Timur": {"lat": -8.657380, "lon": 121.079370},
    "Kalimantan Barat": {"lat": -0.278790, "lon": 111.475290},
    "Kalimantan Tengah": {"lat": -1.681490, "lon": 113.382350},
    "Kalimantan Selatan": {"lat": -3.092640, "lon": 115.283460},
    "Kalimantan Timur": {"lat": 1.693110, "lon": 116.419390},
    "Kalimantan Utara": {"lat": 3.073200, "lon": 116.041300},
    "Sulawesi Utara": {"lat": 0.624690, "lon": 123.975000},
    "Sulawesi Tengah": {"lat": -1.430530, "lon": 121.445450},
    "Sulawesi Selatan": {"lat": -3.669570, "lon": 119.974290},
    "Sulawesi Tenggara": {"lat": -4.144850, "lon": 122.174600},
    "Gorontalo": {"lat": 0.696360, "lon": 122.455630},
    "Sulawesi Barat": {"lat": -2.844130, "lon": 119.232070},
    "Maluku": {"lat": -3.238460, "lon": 130.145270},
    "Maluku Utara": {"lat": 1.570850, "lon": 127.808760},
    "Papua Barat": {"lat": -1.336020, "lon": 133.174050},
    "Papua": {"lat": -4.269280, "lon": 138.080610},
}

# Data populasi provinsi (dalam juta)
PROVINSI_POPULASI = {
    "Aceh": 5.37,
    "Sumatera Utara": 14.80,
    "Sumatera Barat": 5.53,
    "Riau": 6.39,
    "Jambi": 3.62,
    "Sumatera Selatan": 8.47,
    "Bengkulu": 2.01,
    "Lampung": 9.01,
    "Kep. Bangka Belitung": 1.52,
    "Kep. Riau": 2.14,
    "DKI Jakarta": 10.56,
    "Jawa Barat": 49.32,
    "Jawa Tengah": 36.74,
    "DI Yogyakarta": 3.88,
    "Jawa Timur": 40.67,
    "Banten": 12.69,
    "Bali": 4.32,
    "Nusa Tenggara Barat": 5.32,
    "Nusa Tenggara Timur": 5.46,
    "Kalimantan Barat": 5.41,
    "Kalimantan Tengah": 2.66,
    "Kalimantan Selatan": 4.30,
    "Kalimantan Timur": 3.77,
    "Kalimantan Utara": 0.70,
    "Sulawesi Utara": 2.62,
    "Sulawesi Tengah": 3.06,
    "Sulawesi Selatan": 9.07,
    "Sulawesi Tenggara": 2.62,
    "Gorontalo": 1.20,
    "Sulawesi Barat": 1.42,
    "Maluku": 1.85,
    "Maluku Utara": 1.28,
    "Papua Barat": 1.13,
    "Papua": 4.30,
}


def generate_province_simulation(total_cases: int = 6800000) -> pd.DataFrame:
    """
    Generate data simulasi COVID-19 per provinsi.
    
    CATATAN: Ini adalah data SIMULASI untuk tujuan edukasi.
    Data riil per provinsi tidak tersedia dari API publik.
    
    Args:
        total_cases: Total kasus Indonesia untuk distribusi
        
    Returns:
        DataFrame dengan kolom: Provinsi, Kasus, Kematian, Sembuh, Aktif, lat, lon
    """
    import numpy as np
    np.random.seed(42)
    
    rows = []
    
    # Distribusi berdasarkan populasi dengan noise
    total_pop = sum(PROVINSI_POPULASI.values())
    
    for prov, pop in PROVINSI_POPULASI.items():
        # Proporsi berdasarkan populasi + random noise
        base_ratio = pop / total_pop
        noise = np.random.uniform(0.5, 1.5)
        
        # DKI Jakarta dan Jawa cenderung lebih tinggi
        if "Jakarta" in prov or "Jawa" in prov:
            noise *= 1.3
        
        kasus = int(total_cases * base_ratio * noise)
        kematian = int(kasus * np.random.uniform(0.015, 0.030))
        sembuh = int(kasus * np.random.uniform(0.90, 0.98))
        aktif = max(0, kasus - kematian - sembuh)
        
        coords = PROVINSI_COORDS.get(prov, {"lat": 0, "lon": 0})
        
        rows.append({
            "Provinsi": prov,
            "Kasus": kasus,
            "Kematian": kematian,
            "Sembuh": sembuh,
            "Aktif": aktif,
            "Populasi": pop * 1_000_000,
            "Kasus_per_100K": round(kasus / (pop * 10), 2),
            "lat": coords["lat"],
            "lon": coords["lon"],
        })
    
    df = pd.DataFrame(rows)
    df = df.sort_values("Kasus", ascending=False).reset_index(drop=True)
    
    return df


def get_current_stats() -> dict:
    """
    Get statistik COVID-19 Indonesia terkini.
    
    Returns:
        dict dengan total cases, deaths, recovered, active, dll.
    """
    data = fetch_indonesia_current()
    
    if data is None:
        # Fallback ke data terakhir yang diketahui
        return {
            "cases": 6829221,
            "deaths": 162063,
            "recovered": 6647104,
            "active": 20054,
            "critical": 0,
            "cases_per_million": 24466,
            "deaths_per_million": 581,
            "tests": 114158919,
            "population": 279134505,
            "updated": datetime.now().isoformat(),
            "is_fallback": True,
        }
    
    return {
        "cases": data.get("cases", 0),
        "deaths": data.get("deaths", 0),
        "recovered": data.get("recovered", 0),
        "active": data.get("active", 0),
        "critical": data.get("critical", 0),
        "cases_per_million": data.get("casesPerOneMillion", 0),
        "deaths_per_million": data.get("deathsPerOneMillion", 0),
        "tests": data.get("tests", 0),
        "population": data.get("population", 0),
        "updated": datetime.fromtimestamp(data.get("updated", 0) / 1000).isoformat() if data.get("updated") else None,
        "is_fallback": False,
    }


def get_vaccine_df() -> pd.DataFrame:
    """
    Get data vaksinasi sebagai DataFrame.
    
    Returns:
        DataFrame dengan timeline vaksinasi
    """
    data = fetch_vaccine_data()
    
    if data is None or "timeline" not in data:
        return _get_sample_vaccine_df()
    
    rows = []
    for item in data.get("timeline", []):
        try:
            rows.append({
                "Tanggal": pd.to_datetime(item.get("date")),
                "Total_Vaksin": item.get("total", 0),
                "Dosis_Harian": item.get("daily", 0),
            })
        except Exception:
            continue
    
    if not rows:
        return _get_sample_vaccine_df()
    
    df = pd.DataFrame(rows)
    df = df.sort_values("Tanggal").reset_index(drop=True)
    
    return df


def _get_sample_vaccine_df() -> pd.DataFrame:
    """
    Fallback: DataFrame sample vaksinasi.
    """
    import numpy as np
    
    dates = pd.date_range(start="2021-01-13", periods=730, freq="D")
    
    np.random.seed(42)
    
    # Simulasi kurva vaksinasi (sigmoid-like)
    days = np.arange(730)
    max_vaccinated = 200_000_000
    
    # Sigmoid growth
    cumulative = max_vaccinated / (1 + np.exp(-0.015 * (days - 300)))
    daily = np.diff(cumulative, prepend=0) + np.random.normal(0, 10000, 730)
    daily = daily.clip(min=0).astype(int)
    cumulative = np.cumsum(daily)
    
    df = pd.DataFrame({
        "Tanggal": dates,
        "Total_Vaksin": cumulative.astype(int),
        "Dosis_Harian": daily,
    })
    
    return df
