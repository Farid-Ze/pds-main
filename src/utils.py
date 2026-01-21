"""Utility functions untuk COVID-19 Dashboard.

Tujuan file ini:
- Fungsi helper untuk data processing
- Kalkulasi statistik COVID-19
- Formatting dan normalisasi data
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, timedelta


def format_number(num: int | float, decimals: int = 0) -> str:
    """
    Format angka dengan pemisah ribuan.
    
    Args:
        num: Angka yang akan diformat
        decimals: Jumlah desimal
        
    Returns:
        String terformat, contoh: "1.234.567"
    """
    if pd.isna(num):
        return "-"
    
    if decimals > 0:
        return f"{num:,.{decimals}f}".replace(",", ".")
    return f"{int(num):,}".replace(",", ".")


def format_percentage(num: float, decimals: int = 2) -> str:
    """Format sebagai persentase."""
    if pd.isna(num):
        return "-"
    return f"{num:.{decimals}f}%"


def calculate_cfr(deaths: int, cases: int) -> float:
    """
    Hitung Case Fatality Rate (CFR).
    
    CFR = (Total Kematian / Total Kasus) × 100
    
    Args:
        deaths: Total kematian
        cases: Total kasus
        
    Returns:
        CFR dalam persen
    """
    if cases == 0:
        return 0.0
    return (deaths / cases) * 100


def calculate_recovery_rate(recovered: int, cases: int) -> float:
    """
    Hitung Recovery Rate.
    
    Recovery Rate = (Total Sembuh / Total Kasus) × 100
    """
    if cases == 0:
        return 0.0
    return (recovered / cases) * 100


def calculate_active_rate(active: int, cases: int) -> float:
    """
    Hitung Active Case Rate.
    
    Active Rate = (Kasus Aktif / Total Kasus) × 100
    """
    if cases == 0:
        return 0.0
    return (active / cases) * 100


def calculate_rolling_average(df: pd.DataFrame, column: str, window: int = 7) -> pd.Series:
    """
    Hitung rolling average.
    
    Args:
        df: DataFrame dengan data
        column: Nama kolom
        window: Ukuran window (default 7 hari)
        
    Returns:
        Series dengan rolling average
    """
    return df[column].rolling(window=window, min_periods=1).mean()


def calculate_r0_estimate(df: pd.DataFrame, generation_time: int = 5) -> float:
    """
    Estimasi R0 (Basic Reproduction Number) sederhana.
    
    Menggunakan metode ratio pertumbuhan kasus.
    R0 ≈ (kasus hari ini / kasus N hari lalu) ^ (generation_time / N)
    
    Args:
        df: DataFrame dengan kolom 'Kasus_Baru' dan 'Tanggal'
        generation_time: Rata-rata waktu generasi (default 5 hari)
        
    Returns:
        Estimasi R0
    """
    if len(df) < generation_time * 2:
        return 1.0
    
    recent = df.tail(generation_time * 2)
    
    current_avg = recent.tail(generation_time)["Kasus_Baru"].mean()
    previous_avg = recent.head(generation_time)["Kasus_Baru"].mean()
    
    if previous_avg <= 0:
        return 1.0
    
    ratio = current_avg / previous_avg
    r0 = ratio ** (generation_time / generation_time)
    
    return max(0.1, min(10.0, r0))  # Clamp ke range realistis


def calculate_doubling_time(df: pd.DataFrame) -> Optional[float]:
    """
    Hitung doubling time (waktu penggandaan kasus).
    
    Args:
        df: DataFrame dengan kolom 'Kasus'
        
    Returns:
        Doubling time dalam hari atau None
    """
    if len(df) < 14:
        return None
    
    recent = df.tail(14)
    
    start_cases = recent.iloc[0]["Kasus"]
    end_cases = recent.iloc[-1]["Kasus"]
    
    if start_cases <= 0 or end_cases <= start_cases:
        return None
    
    growth_rate = (end_cases / start_cases) ** (1 / 14) - 1
    
    if growth_rate <= 0:
        return None
    
    return np.log(2) / np.log(1 + growth_rate)


def calculate_herd_immunity_threshold(r0: float) -> float:
    """
    Hitung threshold herd immunity.
    
    Herd Immunity Threshold = 1 - (1 / R0)
    
    Args:
        r0: Basic Reproduction Number
        
    Returns:
        Threshold dalam persen
    """
    if r0 <= 1:
        return 0.0
    return (1 - 1 / r0) * 100


def get_trend_direction(df: pd.DataFrame, column: str, days: int = 7) -> str:
    """
    Tentukan arah tren (naik/turun/stabil).
    
    Args:
        df: DataFrame dengan data
        column: Nama kolom
        days: Jumlah hari untuk perbandingan
        
    Returns:
        "naik", "turun", atau "stabil"
    """
    if len(df) < days * 2:
        return "stabil"
    
    recent = df.tail(days * 2)
    
    first_half = recent.head(days)[column].mean()
    second_half = recent.tail(days)[column].mean()
    
    if first_half == 0:
        return "stabil"
    
    change = (second_half - first_half) / first_half
    
    if change > 0.1:
        return "naik"
    elif change < -0.1:
        return "turun"
    return "stabil"


def get_trend_icon(direction: str) -> str:
    """Get icon untuk arah tren."""
    icons = {
        "naik": "📈",
        "turun": "📉",
        "stabil": "➡️",
    }
    return icons.get(direction, "➡️")


def filter_by_date_range(
    df: pd.DataFrame,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    date_column: str = "Tanggal"
) -> pd.DataFrame:
    """
    Filter DataFrame berdasarkan rentang tanggal.
    
    Args:
        df: DataFrame dengan kolom tanggal
        start_date: Tanggal awal (inclusive)
        end_date: Tanggal akhir (inclusive)
        date_column: Nama kolom tanggal
        
    Returns:
        DataFrame yang sudah difilter
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    if start_date is not None:
        result = result[result[date_column] >= pd.Timestamp(start_date)]
    
    if end_date is not None:
        result = result[result[date_column] <= pd.Timestamp(end_date)]
    
    return result


def calculate_statistics(df: pd.DataFrame, column: str) -> dict:
    """
    Hitung statistik lengkap untuk kolom.
    
    Args:
        df: DataFrame
        column: Nama kolom
        
    Returns:
        dict dengan mean, std, min, max, median, q1, q3
    """
    if df.empty or column not in df.columns:
        return {}
    
    series = df[column].dropna()
    
    if len(series) == 0:
        return {}
    
    return {
        "count": len(series),
        "mean": series.mean(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max(),
        "median": series.median(),
        "q1": series.quantile(0.25),
        "q3": series.quantile(0.75),
        "sum": series.sum(),
    }


def get_peak_info(df: pd.DataFrame, column: str = "Kasus_Baru", date_column: str = "Tanggal") -> dict:
    """
    Dapatkan informasi puncak kasus.
    
    Args:
        df: DataFrame
        column: Kolom untuk mencari peak
        date_column: Kolom tanggal
        
    Returns:
        dict dengan date, value dari peak
    """
    if df.empty or column not in df.columns:
        return {"date": None, "value": 0}
    
    idx = df[column].idxmax()
    peak_row = df.loc[idx]
    
    return {
        "date": peak_row[date_column] if date_column in df.columns else None,
        "value": peak_row[column],
    }


def add_date_features(df: pd.DataFrame, date_column: str = "Tanggal") -> pd.DataFrame:
    """
    Tambahkan fitur tanggal ke DataFrame.
    
    Args:
        df: DataFrame dengan kolom tanggal
        date_column: Nama kolom tanggal
        
    Returns:
        DataFrame dengan kolom tambahan: Tahun, Bulan, Hari, Minggu
    """
    if df.empty or date_column not in df.columns:
        return df
    
    result = df.copy()
    result["Tahun"] = result[date_column].dt.year
    result["Bulan"] = result[date_column].dt.month
    result["Nama_Bulan"] = result[date_column].dt.strftime("%B")
    result["Hari"] = result[date_column].dt.day
    result["Minggu"] = result[date_column].dt.isocalendar().week
    result["Hari_Minggu"] = result[date_column].dt.day_name()
    
    return result


# Mapping nama bulan Indonesia
BULAN_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def get_bulan_indonesia(month: int) -> str:
    """Get nama bulan dalam Bahasa Indonesia."""
    return BULAN_ID.get(month, str(month))
