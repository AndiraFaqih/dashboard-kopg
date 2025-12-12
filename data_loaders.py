"""
Modul untuk loading data dari Excel files
Memisahkan logika loading data dari app.py agar lebih modular
"""

import os
import pandas as pd
from functools import lru_cache


# -------------------------------------------------
# KONFIGURASI FILE EXCEL
# -------------------------------------------------
PERBANKAN_DATA_PATH = os.path.join("data", "KINERJA PERBANKAN.xlsx")
NONBANK_DATA_PATH = os.path.join("data", "KINERJA NONBANK.xlsx")


def parse_bulan(x):
    """Parse bulan dari berbagai format (int, float, string) ke int"""
    if isinstance(x, (int, float)) and not pd.isna(x):
        return int(x)
    s = str(x).strip().lower()
    if s.isdigit():
        return int(s)
    s3 = s[:3]
    bulan_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6,
        "jul": 7, "agu": 8, "ags": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
    }
    return bulan_map.get(s3, 1)


def clean_number_series(s):
    """Clean number series dari format Indonesia ke float"""
    return (
        s.astype(str)
        .str.strip()
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )


# -------------------------------------------------
# DATA PERBANKAN
# -------------------------------------------------
@lru_cache(maxsize=1)
def load_perbankan_data(sheet_name="SUMMARY"):
    """Load data utama perbankan dari sheet SUMMARY"""
    df = pd.read_excel(PERBANKAN_DATA_PATH, sheet_name=sheet_name)
    df.columns = df.columns.astype(str).str.strip()

    expected_cols = [
        "Negara", "Provinsi", "Tahun", "Bulan", "Total Aset", "Giro", "Tabungan",
        "Deposito", "Total DPK", "Modal Kerja", "Investasi", "Konsumsi",
        "Total Kredit", "Nominal NPL Gross", "Rasio NPL Gross", "Nominal NPL Net",
        "Rasio NPL Net", "Loan to Deposit Rastio (LDR)",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut belum ada di file: {missing}")

    # Tahun -> int
    df["Tahun"] = df["Tahun"].astype(int)

    # Bulan -> int
    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)

    # Kolom nominal (triliun)
    nominal_cols = [
        "Total Aset", "Giro", "Tabungan", "Deposito", "Total DPK",
        "Modal Kerja", "Investasi", "Konsumsi", "Total Kredit",
        "Nominal NPL Gross", "Nominal NPL Net",
    ]
    for col in nominal_cols:
        if df[col].dtype == object:
            df[col] = clean_number_series(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Rasio di Excel berupa angka persen
    ratio_cols = [
        "Rasio NPL Gross",
        "Rasio NPL Net",
        "Loan to Deposit Rastio (LDR)",
    ]
    for col in ratio_cols:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace("%", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Kolom periode (datetime) untuk sort
    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


@lru_cache(maxsize=1)
def load_umkm_data():
    """Load data UMKM dari sheet PERBANKAN - Per Jenis Usaha"""
    df = pd.read_excel(PERBANKAN_DATA_PATH, sheet_name="PERBANKAN - Per Jenis Usaha")

    # Bersihkan nama kolom
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Cari kolom berdasarkan keyword
    def find_col(keyword, exclude=None):
        cols = list(df.columns)
        candidates = [
            c for c in cols
            if keyword in c and (exclude is None or exclude not in c)
        ]
        if not candidates:
            raise ValueError(
                f"Tidak menemukan kolom yang mengandung '{keyword}'. "
                f"Kolom di file: {cols}"
            )
        return candidates[0]

    prov_col = find_col("Provinsi")
    tahun_col = find_col("Tahun")
    bulan_col = find_col("Bulan")
    jenis_col = find_col("Jenis Kredit")
    kredit_col = find_col("Nominal Kredit")
    npl_col = find_col("Nominal NPL", exclude="Net")
    npl_net_col = find_col("Nominal NPL Net")
    rek_col = find_col("Jumlah Rekening UMKM")

    # Standarkan nama kolom
    df = df.rename(columns={
        prov_col: "Provinsi",
        tahun_col: "Tahun",
        bulan_col: "Bulan",
        jenis_col: "Jenis",
        kredit_col: "Nominal Kredit",
        npl_col: "Nominal NPL",
        npl_net_col: "Nominal NPL Net",
        rek_col: "Jumlah Rekening UMKM",
    })

    # Parsing data
    df["Tahun"] = df["Tahun"].astype(int)
    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)

    nominal_cols = ["Nominal Kredit", "Nominal NPL", "Nominal NPL Net"]
    for col in nominal_cols:
        if df[col].dtype == object:
            df[col] = clean_number_series(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Jumlah rekening
    if df["Jumlah Rekening UMKM"].dtype == object:
        df["Jumlah Rekening UMKM"] = (
            df["Jumlah Rekening UMKM"]
            .astype(str)
            .str.strip()
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
        )
    df["Jumlah Rekening UMKM"] = pd.to_numeric(
        df["Jumlah Rekening UMKM"], errors="coerce"
    ).fillna(0).astype(int)

    # periode untuk sort/agregasi
    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


# -------------------------------------------------
# DATA NON BANK
# -------------------------------------------------
@lru_cache(maxsize=1)
def load_nonbank_data(sheet_name=None):
    """
    Load data non bank dari file KINERJA NONBANK.xlsx
    Jika sheet_name tidak diberikan, akan mencoba load sheet pertama
    """
    if not os.path.exists(NONBANK_DATA_PATH):
        return pd.DataFrame()
    
    # Jika sheet_name tidak diberikan, coba ambil sheet pertama
    if sheet_name is None:
        xl_file = pd.ExcelFile(NONBANK_DATA_PATH)
        sheet_name = xl_file.sheet_names[0] if xl_file.sheet_names else None
        if sheet_name is None:
            return pd.DataFrame()
    
    try:
        df = pd.read_excel(NONBANK_DATA_PATH, sheet_name=sheet_name)
        df.columns = df.columns.astype(str).str.strip()
        
        # Coba parse tahun dan bulan jika ada
        if "Tahun" in df.columns:
            df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce").fillna(0).astype(int)
        if "Bulan" in df.columns:
            df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)
            df["periode"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Bulan"], day=1)
            )
        
        return df
    except Exception as e:
        print(f"Error loading nonbank data: {e}")
        return pd.DataFrame()


def get_nonbank_sheet_names():
    """Get list of sheet names dari file NONBANK"""
    if not os.path.exists(NONBANK_DATA_PATH):
        return []
    try:
        xl_file = pd.ExcelFile(NONBANK_DATA_PATH)
        return xl_file.sheet_names
    except Exception:
        return []

