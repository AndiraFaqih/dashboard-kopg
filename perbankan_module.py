# perbankan_module.py
import os
import pandas as pd
import logging
from db_loaders import (
    load_perbankan_data_from_db,
    load_umkm_data_from_db,
    load_konv_syariah_data_from_db,
)

logger = logging.getLogger(__name__)

# -------------------------------------------------
# KONFIGURASI FILE EXCEL
# -------------------------------------------------
DATA_PATH = os.path.join("data", "KINERJA PERBANKAN.xlsx")
SHEET_NAME = "SUMMARY"  # GANTI dengan nama sheet di Excel


def load_data():
    """
    Versi ini mengikuti PERSIS proses di kode kamu:
    - Setelah df didapat (dari DB atau Excel), barulah:
      * rapikan nama kolom
      * cek expected_cols
      * parse bulan
      * clean angka
      * bentuk kolom 'periode'
    """
    df = None

    # 1) Coba load dari database dulu
    try:
        df = load_perbankan_data_from_db()
        if df is not None and not df.empty:
            logger.info("✅ [PERBANKAN] Data dimuat dari database: %d baris", len(df))
        else:
            df = None
    except Exception as e:
        logger.error("❌ [PERBANKAN] Error loading from DB: %s", e)
        df = None

    # 2) Kalau DB kosong / error → fallback ke Excel
    if df is None:
        df = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
        logger.info("📄 [PERBANKAN] Data dimuat dari Excel: %d baris", len(df))

    # --- MULAI: proses lanjutan PERSIS seperti kode kamu ---

    df.columns = df.columns.astype(str).str.strip()

    expected_cols = [
        "Negara",
        "Provinsi",
        "Tahun",
        "Bulan",
        "Total Aset",
        "Giro",
        "Tabungan",
        "Deposito",
        "Total DPK",
        "Modal Kerja",
        "Investasi",
        "Konsumsi",
        "Total Kredit",
        "Nominal NPL Gross",
        "Rasio NPL Gross",
        "Nominal NPL Net",
        "Rasio NPL Net",
        "Loan to Deposit Rastio (LDR)",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut belum ada di file: {missing}")

    # Tahun -> int
    df["Tahun"] = df["Tahun"].astype(int)

    # Bulan (teks/angka) -> int
    def parse_bulan(x):
        if isinstance(x, (int, float)) and not pd.isna(x):
            return int(x)
        s = str(x).strip().lower()
        if s.isdigit():
            return int(s)
        s3 = s[:3]
        bulan_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "mei": 5,
            "jun": 6,
            "jul": 7,
            "agu": 8,
            "ags": 8,
            "sep": 9,
            "okt": 10,
            "nov": 11,
            "des": 12,
        }
        return bulan_map.get(s3, 1)

    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)

    # Helper: angka Indonesia -> string numerik
    def clean_number_series(s):
        return (
            s.astype(str)
            .str.strip()
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

    # Kolom nominal (triliun)
    nominal_cols = [
        "Total Aset",
        "Giro",
        "Tabungan",
        "Deposito",
        "Total DPK",
        "Modal Kerja",
        "Investasi",
        "Konsumsi",
        "Total Kredit",
        "Nominal NPL Gross",
        "Nominal NPL Net",
    ]
    for col in nominal_cols:
        if df[col].dtype == object:
            df[col] = clean_number_series(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            # Validasi: jika nilai terlalu kecil (< 0.001) atau negatif, set ke 0
        # Juga validasi untuk nilai yang terlalu besar (mungkin error input)
        df[col] = df[col].apply(lambda x: 0.0 if (x < 0.001 or pd.isna(x) or x > 1e15) else x)

    # Rasio di Excel/DB bisa berupa angka persen (misal 3,16) atau desimal (0.0316)
    # Normalisasi: jika > 1, berarti sudah persen, bagi 100; jika <= 1, anggap desimal
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
        # Normalisasi: jika nilai > 1, berarti sudah dalam format persen, bagi 100
        # Jika <= 1, anggap sudah desimal (0.0316 = 3.16%)
        df[col] = df[col].apply(lambda x: x / 100.0 if x > 1.0 else x)

    # Kolom periode (datetime) untuk sort
    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


# -------------------------------------------------
# LOAD DATA UMKM (sheet lain)
# -------------------------------------------------
def load_umkm_data():
    """
    Load sheet UMKM.
    Sekarang: coba dari DB dulu, kalau gagal baru dari Excel,
    tapi seluruh proses setelah df didapat tetap mengikuti kode awal.
    """
    df = None

    # 1) Coba dari database
    try:
        df = load_umkm_data_from_db()
        if df is not None and not df.empty:
            logger.info("✅ [UMKM] Data dimuat dari database: %d baris", len(df))
        else:
            df = None
    except Exception as e:
        logger.error("❌ [UMKM] Error loading from DB: %s", e)
        df = None

    # 2) Fallback ke Excel jika perlu
    if df is None:
        df = pd.read_excel(DATA_PATH, sheet_name="PERBANKAN - Per Jenis Usaha")
        logger.info("📄 [UMKM] Data dimuat dari Excel: %d baris", len(df))

    # --- MULAI: proses lanjutan PERSIS seperti kode kamu ---

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

    df["Tahun"] = df["Tahun"].astype(int)

    def parse_bulan_umkm(x):
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

    df["Bulan"] = df["Bulan"].apply(parse_bulan_umkm).astype(int)

    def clean_num(s):
        return (
            s.astype(str)
             .str.strip()
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)
             .str.replace(",", ".", regex=False)
        )

    nominal_cols = ["Nominal Kredit", "Nominal NPL", "Nominal NPL Net"]
    for col in nominal_cols:
        if df[col].dtype == object:
            df[col] = clean_num(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

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

    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


def load_konv_syariah_data():
    """
    Load data kredit per Skema (Konvensional / Syariah) untuk Bank Umum.
    Hanya ambil baris Kab/Kota yang mengandung kata 'all'.
    Sekarang: coba dari DB dulu, kalau gagal baru Excel.
    """
    df = None

    # 1) Coba dari database
    try:
        df = load_konv_syariah_data_from_db()
        if df is not None and not df.empty:
            logger.info("✅ [KONV-SYARIAH] Data dimuat dari database: %d baris", len(df))
        else:
            df = None
    except Exception as e:
        logger.error("❌ [KONV-SYARIAH] Error loading from DB: %s", e)
        df = None

    # 2) Fallback ke Excel
    if df is None:
        df = pd.read_excel(DATA_PATH, sheet_name="PERBANKAN - Per Daerah")
        logger.info("📄 [KONV-SYARIAH] Data dimuat dari Excel: %d baris", len(df))

    # --- MULAI: proses lanjutan PERSIS seperti kode kamu ---

    # Rapikan nama kolom
    df.columns = df.columns.astype(str).str.strip()

    expected_cols = [
        "Provinsi",
        "Kab/Kota",
        "Tahun",
        "Bulan",
        "Jenis Bank",
        "Skema",
        "Aset",
        "Kredit",
        "DPK",
        "NPL",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut belum ada di sheet Konv-Syariah: {missing}")

    # Hanya Kab/Kota yang mengandung 'all'
    df = df[df["Kab/Kota"].astype(str).str.lower().str.contains("all")].copy()

    # Hanya Bank Umum
    df = df[df["Jenis Bank"].astype(str).str.upper().str.contains("BANK UMUM")].copy()

    # Tahun -> int
    df["Tahun"] = df["Tahun"].astype(int)

    # Bulan -> int
    def parse_bulan_bank(x):
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

    df["Bulan"] = df["Bulan"].apply(parse_bulan_bank).astype(int)

    # helper: angka Indonesia -> float
    def clean_num(s):
        return (
            s.astype(str)
             .str.strip()
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)
             .str.replace(",", ".", regex=False)
        )

    for col in ["Aset", "Kredit", "DPK", "NPL"]:
        if df[col].dtype == object:
            df[col] = clean_num(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # 📌 NORMALISASI SATUAN KREDIT → miliar
    # Kalau nilainya sangat besar, kita asumsi masih Rupiah dan ubah ke miliar
    if df["Kredit"].max() > 1e9:
        df["Kredit"] = df["Kredit"] / 1_000_000_000.0  # Rupiah → miliar

    # periode anchor
    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))

    return df


# -------------------------------------------------
# HELPER AGREGASI & GROWTH
# -------------------------------------------------
def make_agg_month(df_src: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi data per bulan dengan menjumlahkan (sum) semua data untuk Tahun dan Bulan yang sama.
    Ini memastikan bahwa jika ada beberapa record dengan Tahun dan Bulan yang sama
    (misalnya dari provinsi yang berbeda atau data yang di-input beberapa kali),
    mereka akan di-sum, bukan hanya mengambil data terakhir.
    """
    if df_src.empty:
        logger.warning("⚠️  make_agg_month: DataFrame kosong")
        return pd.DataFrame()
    
    # Log jumlah baris sebelum agregasi
    logger.info(f"📊 make_agg_month: Agregasi {len(df_src)} baris data")
    
    # Agregasi untuk kolom nominal (sum) - menjumlahkan semua data dengan Tahun dan Bulan yang sama
    # Untuk rasio, ambil rata-rata (mean) dari database
    agg = df_src.groupby(["Tahun", "Bulan"], as_index=False).agg(
        {
            "Total Aset": "sum",
            "Total DPK": "sum",
            "Total Kredit": "sum",
            "Giro": "sum",
            "Tabungan": "sum",
            "Deposito": "sum",
            "Modal Kerja": "sum",
            "Investasi": "sum",
            "Konsumsi": "sum",
            "Nominal NPL Gross": "sum",
            "Nominal NPL Net": "sum",
            "Rasio NPL Gross": "mean",  # Ambil rata-rata dari database
            "Rasio NPL Net": "mean",  # Ambil rata-rata dari database
            "Loan to Deposit Rastio (LDR)": "mean",  # Ambil rata-rata dari database
        }
    )
    
    # Log jumlah baris setelah agregasi
    logger.info(f"📊 make_agg_month: Setelah agregasi: {len(agg)} baris (per Tahun-Bulan)")
    
    agg["periode"] = pd.to_datetime(
        dict(year=agg["Tahun"], month=agg["Bulan"], day=1)
    )
    
    # Sort by periode untuk memastikan urutan yang benar
    agg = agg.sort_values("periode")
    
    return agg


def compute_growth(
    agg: pd.DataFrame,
    metric: str,
    selected_year: int | None,
    selected_month: int | None,
):
    """
    Menghitung nilai current, YoY, dan YtD untuk metric tertentu.
    Menggunakan filter tahun/bulan jika dipilih, atau data terakhir jika tidak ada filter.
    """
    if agg.empty or metric not in agg.columns:
        logger.warning(f"⚠️  compute_growth: DataFrame kosong atau metric '{metric}' tidak ditemukan")
        return 0.0, None, None

    agg = agg.sort_values("periode")
    current = None

    # Jika ada filter tahun, gunakan data dari tahun tersebut
    if selected_year is not None:
        year_df = agg[agg["Tahun"] == selected_year].sort_values("periode")
        if selected_month is not None:
            # Filter tahun + bulan: ambil data bulan tersebut atau bulan terakhir sebelum bulan tersebut
            ym = year_df[year_df["Bulan"] == selected_month]
            if not ym.empty:
                current = ym.iloc[-1]
                logger.info(f"📊 compute_growth: Menggunakan data {selected_year}-{selected_month:02d} untuk {metric}")
            else:
                # Jika bulan tidak ada, ambil bulan terakhir sebelum bulan tersebut
                le = year_df[year_df["Bulan"] <= selected_month]
                if not le.empty:
                    current = le.iloc[-1]
                    logger.info(f"📊 compute_growth: Bulan {selected_month} tidak ada, menggunakan bulan terakhir sebelum {selected_month} untuk {metric}")
        else:
            # Filter tahun saja: ambil data terakhir dari tahun tersebut
            if not year_df.empty:
                current = year_df.iloc[-1]
                logger.info(f"📊 compute_growth: Menggunakan data terakhir dari tahun {selected_year} untuk {metric}")

    # Jika tidak ada filter atau tidak ada data sesuai filter, ambil data terakhir
    if current is None:
        if not agg.empty:
            current = agg.iloc[-1]
            logger.info(f"📊 compute_growth: Tidak ada filter, menggunakan data terakhir (periode: {current['periode']}) untuk {metric}")
        else:
            logger.warning(f"⚠️  compute_growth: DataFrame kosong setelah filter")
            return 0.0, None, None

    curr_year = int(current["Tahun"])
    curr_month = int(current["Bulan"])
    curr_val = float(current[metric]) if pd.notna(current[metric]) else 0.0
    
    # Validasi: jika nilai terlalu kecil atau tidak valid, return 0
    if curr_val < 0 or pd.isna(curr_val):
        curr_val = 0.0

    yoy = None
    prev_yoy = agg[(agg["Tahun"] == curr_year - 1) & (agg["Bulan"] == curr_month)]
    if not prev_yoy.empty:
        prev_val = float(prev_yoy.iloc[0][metric]) if pd.notna(prev_yoy.iloc[0][metric]) else 0.0
        if prev_val > 0 and curr_val >= 0:
            yoy = ((curr_val - prev_val) / prev_val) * 100.0
            # Validasi: jika growth terlalu ekstrem (> 10000% atau < -100%), mungkin data salah
            if abs(yoy) > 10000:
                yoy = None

    ytd = None
    same_year = agg[agg["Tahun"] == curr_year].sort_values("periode")
    if not same_year.empty and len(same_year) > 1:
        first_row = same_year.iloc[0]
        prev_val = float(first_row[metric]) if pd.notna(first_row[metric]) else 0.0
        if prev_val > 0 and curr_val >= 0:
            ytd = ((curr_val - prev_val) / prev_val) * 100.0
            # Validasi: jika growth terlalu ekstrem, mungkin data salah
            if abs(ytd) > 10000:
                ytd = None

    return curr_val, yoy, ytd


def growth_class(v: float | None) -> str:
    if v is None:
        return "secondary"
    if abs(v) < 1e-9:
        return "secondary"
    return "success" if v >= 0 else "danger"


# -------------------------------------------------
# FUNCTION PEMBANGUN CONTEXT DASHBOARD PERBANKAN
# (isi sama persis dengan body route `dashboard` sebelumnya)
# -------------------------------------------------
def build_dashboard_context(request):
    # ---------- Data utama ----------
    df = load_data()

    negara_list = sorted(df["Negara"].dropna().unique().tolist())
    provinsi_list = sorted(df["Provinsi"].dropna().unique().tolist())
    tahun_list = sorted(df["Tahun"].dropna().unique().tolist())
    bulan_list = sorted(df["Bulan"].dropna().unique().tolist())

    negara = request.args.get("negara") or ""
    provinsi = request.args.get("provinsi") or ""
    tahun = request.args.get("tahun") or ""
    bulan = request.args.get("bulan") or ""
    interval = request.args.get("interval") or "bulanan"

    selected_year = int(tahun) if tahun else None
    selected_month = int(bulan) if bulan else None

    # Filter wilayah data utama
    df_region = df.copy()
    logger.info(f"📊 build_dashboard_context: Total data sebelum filter: {len(df_region)} baris")
    
    if negara:
        df_region = df_region[df_region["Negara"] == negara]
        logger.info(f"📊 build_dashboard_context: Setelah filter negara '{negara}': {len(df_region)} baris")
    if provinsi:
        df_region = df_region[df_region["Provinsi"] == provinsi]
        logger.info(f"📊 build_dashboard_context: Setelah filter provinsi '{provinsi}': {len(df_region)} baris")
    if df_region.empty:
        df_region = df.copy()
        logger.warning("⚠️  Filter menghasilkan data kosong, menggunakan semua data")
    
    # Validasi: cek apakah ada data yang valid
    if df_region.empty:
        logger.warning("⚠️  Tidak ada data untuk filter yang dipilih")
        # Return default values
        return {
            "aset_val": 0.0, "aset_yoy": None, "aset_ytd": None,
            "kredit_val": 0.0, "kredit_yoy": None, "kredit_ytd": None,
            "dpk_val": 0.0, "dpk_yoy": None, "dpk_ytd": None,
            "npl_val": 0.0, "npl_yoy": None, "npl_ytd": None,
        }

    # Agregasi data per bulan - menjumlahkan semua data dengan Tahun dan Bulan yang sama
    agg_month_region = make_agg_month(df_region)
    logger.info(f"📊 build_dashboard_context: Setelah agregasi per bulan: {len(agg_month_region)} baris")
    
    # Validasi: cek apakah data terlalu seragam (mungkin data test)
    if not agg_month_region.empty:
        sample_row = agg_month_region.iloc[-1]
        aset = float(sample_row.get("Total Aset", 0))
        kredit = float(sample_row.get("Total Kredit", 0))
        dpk = float(sample_row.get("Total DPK", 0))
        
        # Jika semua nilai sama (misalnya semua 123), mungkin data test
        # Hapus data yang terdeteksi sebagai test data
        if aset > 0 and abs(aset - kredit) < 0.01 and abs(aset - dpk) < 0.01 and aset < 1000:
            logger.warning(f"⚠️  Data terdeteksi mungkin data test (nilai sama: {aset}). Mengabaikan data ini.")
            # Hapus baris yang terdeteksi sebagai test data
            mask = ~(
                (agg_month_region["Total Aset"] == aset) & 
                (agg_month_region["Total Kredit"] == kredit) & 
                (agg_month_region["Total DPK"] == dpk)
            )
            agg_month_region = agg_month_region[mask]
            if agg_month_region.empty:
                logger.warning("⚠️  Semua data terdeteksi sebagai test data. Menggunakan data kosong.")
                agg_month_region = pd.DataFrame(columns=df_region.columns)

    # Tambahan kolom Kredit Produktif & Konsumtif
    agg_month_region["Kredit Produktif"] = (
        agg_month_region["Modal Kerja"] + agg_month_region["Investasi"]
    )
    agg_month_region["Kredit Konsumtif"] = agg_month_region["Konsumsi"]

    # ---------- KPI utama ----------
    aset_val, aset_yoy, aset_ytd = compute_growth(
        agg_month_region, "Total Aset", selected_year, selected_month
    )
    dpk_val, dpk_yoy, dpk_ytd = compute_growth(
        agg_month_region, "Total DPK", selected_year, selected_month
    )
    kredit_val, kredit_yoy, kredit_ytd = compute_growth(
        agg_month_region, "Total Kredit", selected_year, selected_month
    )
    npl_raw, npl_yoy, npl_ytd = compute_growth(
        agg_month_region, "Rasio NPL Gross", selected_year, selected_month
    )
    ldr_raw, ldr_yoy, ldr_ytd = compute_growth(
        agg_month_region, "Loan to Deposit Rastio (LDR)", selected_year, selected_month
    )

    # npl_raw & ldr_raw disimpan sebagai desimal → untuk kartu & chart: ×100 jadi persen
    # Pastikan nilai valid sebelum dikalikan
    npl_val = (npl_raw * 100) if npl_raw is not None and npl_raw >= 0 else 0.0
    ldr_val = (ldr_raw * 100) if ldr_raw is not None and ldr_raw >= 0 else 0.0
    
    # Validasi: jika nilai terlalu ekstrem, mungkin ada masalah data
    if npl_val > 1000:  # NPL > 1000% tidak masuk akal
        logger.warning(f"⚠️  NPL Gross terlalu tinggi: {npl_val}%. Memeriksa data...")
        npl_val = 0.0
        npl_yoy = None
        npl_ytd = None
    
    # Log untuk debugging
    logger.info(f"📊 KPI Values - Aset: {aset_val:.2f}T, Kredit: {kredit_val:.2f}T, DPK: {dpk_val:.2f}T, NPL: {npl_val:.2f}%")

    # ---------- DPK components ----------
    giro_val, giro_yoy, giro_ytd = compute_growth(
        agg_month_region, "Giro", selected_year, selected_month
    )
    tab_val, tab_yoy, tab_ytd = compute_growth(
        agg_month_region, "Tabungan", selected_year, selected_month
    )
    dep_val, dep_yoy, dep_ytd = compute_growth(
        agg_month_region, "Deposito", selected_year, selected_month
    )

    share_giro = share_tab = share_dep = 0.0
    if dpk_val != 0:
        share_giro = giro_val / dpk_val * 100.0
        share_tab = tab_val / dpk_val * 100.0
        share_dep = dep_val / dpk_val * 100.0

    # ---------- Kredit Produktif vs Konsumtif ----------
    konsumtif_val, konsumtif_yoy, konsumtif_ytd = compute_growth(
        agg_month_region, "Kredit Konsumtif", selected_year, selected_month
    )
    produktif_val, produktif_yoy, produktif_ytd = compute_growth(
        agg_month_region, "Kredit Produktif", selected_year, selected_month
    )

    share_kons = share_prod = 0.0
    if kredit_val != 0:
        share_kons = konsumtif_val / kredit_val * 100.0
        share_prod = produktif_val / kredit_val * 100.0

    mk_val, _, _ = compute_growth(
        agg_month_region, "Modal Kerja", selected_year, selected_month
    )
    inv_val, _, _ = compute_growth(
        agg_month_region, "Investasi", selected_year, selected_month
    )

    share_mk = share_inv = 0.0
    if produktif_val != 0:
        share_mk = mk_val / produktif_val * 100.0
        share_inv = inv_val / produktif_val * 100.0

    # ---------- Chart tahunan Giro / Tabungan / Deposito ----------
    agg_year = (
        agg_month_region.groupby(["Tahun"], as_index=False)
        .agg({
            "Giro": "sum",
            "Tabungan": "sum",
            "Deposito": "sum",
        })
        .sort_values("Tahun")
    )

    year_labels = agg_year["Tahun"].astype(str).tolist()
    year_giro_series = agg_year["Giro"].tolist()
    year_tab_series = agg_year["Tabungan"].tolist()
    year_dep_series = agg_year["Deposito"].tolist()

    # ---------- Mini bar: 3 periode terakhir (sesuai interval) ----------
    agg_for_chart = agg_month_region.copy()
    if selected_year is not None:
        if selected_month is not None:
            cond = (agg_for_chart["Tahun"] < selected_year) | (
                (agg_for_chart["Tahun"] == selected_year)
                & (agg_for_chart["Bulan"] <= selected_month)
            )
            agg_for_chart = agg_for_chart[cond]
        else:
            agg_for_chart = agg_for_chart[agg_for_chart["Tahun"] <= selected_year]
    if agg_for_chart.empty:
        agg_for_chart = agg_month_region.copy()

    if interval == "triwulan":
        tmp = agg_for_chart.copy()
        tmp["Triwulan"] = ((tmp["Bulan"] - 1) // 3) + 1
        tmp = (
            tmp.groupby(["Tahun", "Triwulan"], as_index=False)
            .agg(
                {
                    "Total Aset": "sum",
                    "Total DPK": "sum",
                    "Total Kredit": "sum",
                }
            )
        )
        tmp["periode_label"] = pd.to_datetime(
            dict(year=tmp["Tahun"], month=tmp["Triwulan"] * 3, day=1)
        )
        base_labels = tmp["periode_label"].dt.strftime("%b '%y").tolist()
        base_aset = tmp["Total Aset"].tolist()
        base_dpk = tmp["Total DPK"].tolist()
        base_kredit = tmp["Total Kredit"].tolist()
    elif interval == "semesteran":
        tmp = agg_for_chart.copy()
        tmp["Semester"] = tmp["Bulan"].apply(lambda m: 1 if m <= 6 else 2)
        tmp = (
            tmp.groupby(["Tahun", "Semester"], as_index=False)
            .agg(
                {
                    "Total Aset": "sum",
                    "Total DPK": "sum",
                    "Total Kredit": "sum",
                }
            )
        )
        tmp["periode_label"] = pd.to_datetime(
            dict(year=tmp["Tahun"], month=tmp["Semester"] * 6, day=1)
        )
        base_labels = tmp["periode_label"].dt.strftime("%b '%y").tolist()
        base_aset = tmp["Total Aset"].tolist()
        base_dpk = tmp["Total DPK"].tolist()
        base_kredit = tmp["Total Kredit"].tolist()
    elif interval == "tahunan":
        tmp = (
            agg_for_chart.groupby(["Tahun"], as_index=False)
            .agg(
                {
                    "Total Aset": "sum",
                    "Total DPK": "sum",
                    "Total Kredit": "sum",
                }
            )
            .sort_values("Tahun")
        )
        base_labels = tmp["Tahun"].astype(str).tolist()
        base_aset = tmp["Total Aset"].tolist()
        base_dpk = tmp["Total DPK"].tolist()
        base_kredit = tmp["Total Kredit"].tolist()
    else:  # bulanan
        tmp = agg_for_chart.copy()
        base_labels = tmp["periode"].dt.strftime("%b '%y").tolist()
        base_aset = tmp["Total Aset"].tolist()
        base_dpk = tmp["Total DPK"].tolist()
        base_kredit = tmp["Total Kredit"].tolist()

    if len(base_labels) >= 3:
        mini_labels = base_labels[-3:]
        mini_aset = base_aset[-3:]
        mini_dpk = base_dpk[-3:]
        mini_kredit = base_kredit[-3:]
    else:
        mini_labels = base_labels
        mini_aset = base_aset
        mini_dpk = base_dpk
        mini_kredit = base_kredit

    # ---------- NPL & LDR tahunan (Desember, semua tahun) ----------
    # Khusus untuk 2 grafik ini: tidak mengikuti filter, hanya ambil nilai Desember di Sumatra Selatan
    # AMBIL LANGSUNG DARI DATABASE tanpa normalisasi atau perhitungan apapun
    from db_loaders import get_db_session
    from sqlalchemy import text
    
    npl_labels = []
    npl_series = []
    ldr_series = []
    
    try:
        session = get_db_session()
        # Query langsung ke database untuk mendapatkan nilai asli tanpa normalisasi
        # Kolom "Bulan" di database adalah string, jadi ambil semua dulu lalu filter di Python
        query = text("""
            SELECT 
                "Tahun",
                "Bulan",
                "Provinsi",
                "Rasio NPL Gross",
                "Loan to Deposit Rastio (LDR)"
            FROM kinerja_perbankan_summary
            WHERE (
                UPPER(TRIM("Provinsi")) LIKE '%SUMATERA SELATAN%'
                OR UPPER(TRIM("Provinsi")) LIKE '%SUMATERASELATAN%'
                OR UPPER(TRIM("Provinsi")) LIKE '%SUMSEL%'
            )
            ORDER BY "Tahun", "Bulan"
        """)
        df_raw = pd.read_sql(query, session.bind)

        session.close()
        
        if not df_raw.empty:
            # Parse Bulan untuk memastikan hanya ambil data Desember (bulan 12)
            # Handle berbagai format: 12, '12', 'Desember', 'Des', dll
            from db_loaders import parse_bulan_from_db
            if df_raw["Bulan"].dtype == object:
                df_raw["Bulan"] = df_raw["Bulan"].apply(parse_bulan_from_db).astype(int)
            elif df_raw["Bulan"].dtype not in [int, 'int64', 'int32']:
                df_raw["Bulan"] = df_raw["Bulan"].apply(parse_bulan_from_db).astype(int)
            
            # Filter hanya bulan Desember (12)
            df_raw = df_raw[df_raw["Bulan"] == 12]          
            # Sort by tahun
            df_raw = df_raw.sort_values("Tahun")
            # Jika ada duplikat tahun, ambil yang pertama
            df_raw = df_raw.drop_duplicates(subset=["Tahun"], keep="first")
            
            # Ambil nilai langsung dari database, TANPA perhitungan apapun
            # Nilai di database dalam format desimal (0.0316 = 3.16%), jadi perlu dikalikan 100 untuk display
            npl_series = df_raw["Rasio NPL Gross"].fillna(0.0).astype(float).tolist()
            ldr_series = df_raw["Loan to Deposit Rastio (LDR)"].fillna(0.0).astype(float).tolist()
            
            npl_labels = [f"Des'{str(y)[-2:]}" for y in df_raw["Tahun"]]

            # Konversi dari desimal ke persen (kalikan 100) untuk display di grafik
            npl_series = [x * 100 for x in npl_series]
            ldr_series = [x * 100 for x in ldr_series]
                
            logger.info(f"📊 NPL/LDR Trend - Mengambil {len(npl_labels)} data Desember dari Sumatra Selatan langsung dari DB (tanpa perhitungan)")
            logger.info(f"   Tahun: {df_raw['Tahun'].tolist()}")
            logger.info(f"   NPL: {npl_series}")
            logger.info(f"   LDR: {ldr_series}")
        else:
            logger.warning("⚠️  Tidak ada data Desember untuk Sumatra Selatan di database")
            npl_labels = []
            npl_series = []
            ldr_series = []
    except Exception as e:
        logger.error(f"❌ Error mengambil data NPL/LDR dari database: {e}")
        npl_labels = []
        npl_series = []
        ldr_series = []

    # -------------------------------------------------
    # DATA UMKM
    # -------------------------------------------------
    df_umkm = load_umkm_data()

    umkm_region = df_umkm.copy()
    if provinsi:
        prov_norm = provinsi.strip().upper()
        tmp = umkm_region[umkm_region["Provinsi"].astype(str).str.upper() == prov_norm]
        # kalau ketemu, pakai yang match; kalau tidak, biarkan
        if not tmp.empty:
            umkm_region = tmp

    agg_umkm = (
        umkm_region.groupby(["Tahun", "Bulan"], as_index=False)
        .agg(
            {
                "Nominal Kredit": "sum",
                "Nominal NPL": "sum",
                "Nominal NPL Net": "sum",
                "Jumlah Rekening UMKM": "sum",
            }
        )
        .sort_values(["Tahun", "Bulan"])
    )
    agg_umkm["periode"] = pd.to_datetime(
        dict(year=agg_umkm["Tahun"], month=agg_umkm["Bulan"], day=1)
    )

    # -------------------------------------------------
    # PIE: Kredit UMKM vs Non-UMKM (anchor periode)
    # -------------------------------------------------
    umkm_share_labels = []
    umkm_share_values = []
    umkm_pie_umkm_tril = 0.0
    umkm_pie_non_tril = 0.0

    umkm_anchor = umkm_region.copy()
    if selected_year is not None:
        umkm_anchor = umkm_anchor[umkm_anchor["Tahun"] == selected_year]
    if selected_month is not None:
        umkm_anchor = umkm_anchor[umkm_anchor["Bulan"] == selected_month]

    if umkm_anchor.empty and not umkm_region.empty:
        last_periode = umkm_region["periode"].max()
        umkm_anchor = umkm_region[umkm_region["periode"] == last_periode]

    if not umkm_anchor.empty:
        pie_raw = (
            umkm_anchor.groupby("Jenis", as_index=False)["Nominal Kredit"].sum()
        )

        def normalize_kat(j):
            s = str(j).strip().upper()
            if "NON" in s and "UMKM" in s:
                return "Non-UMKM"
            elif "UMKM" in s:
                return "UMKM"
            else:
                return s.title()

        pie_raw["Kategori"] = pie_raw["Jenis"].apply(normalize_kat)
        pie_agg = pie_raw.groupby("Kategori", as_index=False)["Nominal Kredit"].sum()

        for cat in ["Non-UMKM", "UMKM"]:
            row = pie_agg[pie_agg["Kategori"] == cat]
            if not row.empty:
                val = float(row["Nominal Kredit"].iloc[0])
                umkm_share_labels.append(cat)
                umkm_share_values.append(val)
                if cat == "UMKM":
                    umkm_pie_umkm_tril = val / 1000.0
                else:
                    umkm_pie_non_tril = val / 1000.0

        # kalau suatu saat ada kategori lain di luar UMKM & Non-UMKM
        others = pie_agg[~pie_agg["Kategori"].isin(["Non-UMKM", "UMKM"])]
        for _, r in others.iterrows():
            umkm_share_labels.append(r["Kategori"])
            umkm_share_values.append(float(r["Nominal Kredit"]))

    # turunan rasio & produktivitas
    agg_umkm["NPL Ratio"] = 0.0
    mask_kredit = agg_umkm["Nominal Kredit"] != 0
    agg_umkm.loc[mask_kredit, "NPL Ratio"] = (
        agg_umkm.loc[mask_kredit, "Nominal NPL"]
        / agg_umkm.loc[mask_kredit, "Nominal Kredit"]
        * 100.0
    )

    agg_umkm["Kredit per Rekening"] = 0.0
    mask_rek = agg_umkm["Jumlah Rekening UMKM"] != 0
    agg_umkm.loc[mask_rek, "Kredit per Rekening"] = (
        agg_umkm.loc[mask_rek, "Nominal Kredit"]
        / agg_umkm.loc[mask_rek, "Jumlah Rekening UMKM"]
    )

    # KPI kartu UMKM
    umkm_kredit_val, umkm_kredit_yoy, umkm_kredit_ytd = compute_growth(
        agg_umkm, "Nominal Kredit", selected_year, selected_month
    )
    umkm_npl_val, umkm_npl_yoy, umkm_npl_ytd = compute_growth(
        agg_umkm, "Nominal NPL", selected_year, selected_month
    )
    umkm_npl_net_val, umkm_npl_net_yoy, umkm_npl_net_ytd = compute_growth(
        agg_umkm, "Nominal NPL Net", selected_year, selected_month
    )
    umkm_rek_val, umkm_rek_yoy, umkm_rek_ytd = compute_growth(
        agg_umkm, "Jumlah Rekening UMKM", selected_year, selected_month
    )
    umkm_npl_ratio_val, umkm_npl_ratio_yoy, umkm_npl_ratio_ytd = compute_growth(
        agg_umkm, "NPL Ratio", selected_year, selected_month
    )
    umkm_kpr_val, umkm_kpr_yoy, umkm_kpr_ytd = compute_growth(
        agg_umkm, "Kredit per Rekening", selected_year, selected_month
    )

    agg_umkm_year = (
        agg_umkm.groupby("Tahun", as_index=False)
        .agg(
            {
                "Nominal Kredit": "sum",
                "NPL Ratio": "mean",
                "Kredit per Rekening": "mean",
            }
        )
        .sort_values("Tahun")
    )
    umkm_year_labels = agg_umkm_year["Tahun"].astype(str).tolist()
    umkm_year_kredit = agg_umkm_year["Nominal Kredit"].tolist()
    umkm_year_npl_ratio = agg_umkm_year["NPL Ratio"].tolist()
    umkm_year_kpr = agg_umkm_year["Kredit per Rekening"].tolist()

    # -------------------------------------------------
    # KREDIT KONVENSIONAL vs SYARIAH (Bank Umum)
    # -------------------------------------------------
    df_ks = load_konv_syariah_data()  # fungsi ini sudah HANYA ambil Kab/Kota yang ada "all"

    ks_region = df_ks.copy()
    if provinsi:
        prov_norm = provinsi.strip().upper()
        tmp = ks_region[ks_region["Provinsi"].astype(str).str.upper() == prov_norm]
        # kalau ketemu, pakai provinsi tsb; kalau tidak, biarkan tetap nasional
        if not tmp.empty:
            ks_region = tmp

    # Anchor: ikut filter tahun & bulan
    ks_anchor = ks_region.copy()
    if selected_year is not None:
        ks_anchor = ks_anchor[ks_anchor["Tahun"] == selected_year]
    if selected_month is not None:
        ks_anchor = ks_anchor[ks_anchor["Bulan"] == selected_month]

    # Kalau filter bikin kosong, pakai periode terakhir yang ada
    if ks_anchor.empty and not ks_region.empty:
        last_periode = ks_region["periode"].max()
        ks_anchor = ks_region[ks_region["periode"] == last_periode]

    ks_share_labels = []
    ks_share_values = []
    ks_konv_tril = 0.0
    ks_syar_tril = 0.0

    if not ks_anchor.empty:
        def norm_skema(s):
            u = str(s).strip().upper()
            if "KONV" in u:
                return "Konvensional"
            if "SYAR" in u:
                return "Syariah"
            return s.title()

        ks_anchor["Kategori"] = ks_anchor["Skema"].apply(norm_skema)
        pie_agg = ks_anchor.groupby("Kategori", as_index=False)["Kredit"].sum()

        # Nilai Kredit di sheet ini kita anggap dalam satuan MILIAR
        konv_val = float(
            pie_agg.loc[pie_agg["Kategori"] == "Konvensional", "Kredit"].sum()
        )
        syar_val = float(
            pie_agg.loc[pie_agg["Kategori"] == "Syariah", "Kredit"].sum()
        )

        total_val = konv_val + syar_val
        if total_val > 0:
            # Data untuk PIE (pakai satuan miliar, yg penting proporsinya)
            ks_share_labels = ["Konvensional", "Syariah"]
            ks_share_values = [konv_val, syar_val]

            # KONVERSI: miliar → triliun untuk ditampilkan di kartu
            ks_konv_tril = konv_val / 1000.0
            ks_syar_tril = syar_val / 1000.0

    # -------------------------------------------------
    # CONTEXT UNTUK TEMPLATE
    # -------------------------------------------------
    ctx = dict(
        negara_list=negara_list,
        provinsi_list=provinsi_list,
        tahun_list=tahun_list,
        bulan_list=bulan_list,
        negara_selected=negara,
        provinsi_selected=provinsi,
        tahun_selected=tahun,
        bulan_selected=bulan,
        interval_selected=interval,
        # KPI utama
        aset_val=aset_val,
        aset_yoy=aset_yoy,
        aset_ytd=aset_ytd,
        aset_yoy_class=growth_class(aset_yoy),
        aset_ytd_class=growth_class(aset_ytd),
        dpk_val=dpk_val,
        dpk_yoy=dpk_yoy,
        dpk_ytd=dpk_ytd,
        dpk_yoy_class=growth_class(dpk_yoy),
        dpk_ytd_class=growth_class(dpk_ytd),
        kredit_val=kredit_val,
        kredit_yoy=kredit_yoy,
        kredit_ytd=kredit_ytd,
        kredit_yoy_class=growth_class(kredit_yoy),
        kredit_ytd_class=growth_class(kredit_ytd),
        npl_val=npl_val,
        npl_yoy=npl_yoy,
        npl_ytd=npl_ytd,
        npl_yoy_class=growth_class(npl_yoy),
        npl_ytd_class=growth_class(npl_ytd),
        ldr_val=ldr_val,
        ldr_yoy=ldr_yoy,
        ldr_ytd=ldr_ytd,
        ldr_yoy_class=growth_class(ldr_yoy),
        ldr_ytd_class=growth_class(ldr_ytd),
        # Giro/Tab/Deposito
        giro_val=giro_val,
        giro_yoy=giro_yoy,
        giro_ytd=giro_ytd,
        giro_yoy_class=growth_class(giro_yoy),
        giro_ytd_class=growth_class(giro_ytd),
        tab_val=tab_val,
        tab_yoy=tab_yoy,
        tab_ytd=tab_ytd,
        tab_yoy_class=growth_class(tab_yoy),
        tab_ytd_class=growth_class(tab_ytd),
        dep_val=dep_val,
        dep_yoy=dep_yoy,
        dep_ytd=dep_ytd,
        dep_yoy_class=growth_class(dep_yoy),
        dep_ytd_class=growth_class(dep_ytd),
        share_giro=share_giro,
        share_tab=share_tab,
        share_dep=share_dep,
        # Kredit produktif/konsumtif
        konsumtif_val=konsumtif_val,
        konsumtif_yoy=konsumtif_yoy,
        konsumtif_ytd=konsumtif_ytd,
        konsumtif_yoy_class=growth_class(konsumtif_yoy),
        konsumtif_ytd_class=growth_class(konsumtif_ytd),
        produktif_val=produktif_val,
        produktif_yoy=produktif_yoy,
        produktif_ytd=produktif_ytd,
        produktif_yoy_class=growth_class(produktif_yoy),
        produktif_ytd_class=growth_class(produktif_ytd),
        share_kons=share_kons,
        share_prod=share_prod,
        mk_val=mk_val,
        inv_val=inv_val,
        share_mk=share_mk,
        share_inv=share_inv,
        # Chart tahunan Giro / Tabungan / Deposito
        year_labels=year_labels,
        year_giro_series=year_giro_series,
        year_tab_series=year_tab_series,
        year_dep_series=year_dep_series,
        # Mini bar 3 periode
        mini_labels=mini_labels,
        mini_aset=mini_aset,
        mini_dpk=mini_dpk,
        mini_kredit=mini_kredit,
        # NPL & LDR tahunan Desember
        npl_labels=npl_labels,
        npl_series=npl_series,
        ldr_series=ldr_series,
        # KPI UMKM
        umkm_kredit_val=umkm_kredit_val,
        umkm_kredit_yoy=umkm_kredit_yoy,
        umkm_kredit_ytd=umkm_kredit_ytd,
        umkm_kredit_yoy_class=growth_class(umkm_kredit_yoy),
        umkm_kredit_ytd_class=growth_class(umkm_kredit_ytd),
        umkm_npl_val=umkm_npl_val,
        umkm_npl_yoy=umkm_npl_yoy,
        umkm_npl_ytd=umkm_npl_ytd,
        umkm_npl_yoy_class=growth_class(umkm_npl_yoy),
        umkm_npl_ytd_class=growth_class(umkm_npl_ytd),
        umkm_npl_net_val=umkm_npl_net_val,
        umkm_npl_net_yoy=umkm_npl_net_yoy,
        umkm_npl_net_ytd=umkm_npl_net_ytd,
        umkm_npl_net_yoy_class=growth_class(umkm_npl_net_yoy),
        umkm_npl_net_ytd_class=growth_class(umkm_npl_net_ytd),
        umkm_rek_val=umkm_rek_val,
        umkm_rek_yoy=umkm_rek_yoy,
        umkm_rek_ytd=umkm_rek_ytd,
        umkm_rek_yoy_class=growth_class(umkm_rek_yoy),
        umkm_rek_ytd_class=growth_class(umkm_rek_ytd),
        umkm_npl_ratio_val=umkm_npl_ratio_val,
        umkm_npl_ratio_yoy=umkm_npl_ratio_yoy,
        umkm_npl_ratio_ytd=umkm_npl_ratio_ytd,
        umkm_npl_ratio_yoy_class=growth_class(umkm_npl_ratio_yoy),
        umkm_npl_ratio_ytd_class=growth_class(umkm_npl_ratio_ytd),
        umkm_kpr_val=umkm_kpr_val,
        umkm_kpr_yoy=umkm_kpr_yoy,
        umkm_kpr_ytd=umkm_kpr_ytd,
        umkm_kpr_yoy_class=growth_class(umkm_kpr_yoy),
        umkm_kpr_ytd_class=growth_class(umkm_kpr_ytd),
        # Chart tahunan UMKM
        umkm_year_labels=umkm_year_labels,
        umkm_year_kredit=umkm_year_kredit,
        umkm_year_npl_ratio=umkm_year_npl_ratio,
        umkm_year_kpr=umkm_year_kpr,
        # Pie Kredit Konvensional vs Syariah
        ks_share_labels=ks_share_labels,
        ks_share_values=ks_share_values,
        ks_konv_tril=ks_konv_tril,
        ks_syar_tril=ks_syar_tril,
        # Pie Kredit UMKM vs Non-UMKM
        umkm_share_labels=umkm_share_labels,
        umkm_share_values=umkm_share_values,
        umkm_pie_umkm_tril=umkm_pie_umkm_tril,
        umkm_pie_non_tril=umkm_pie_non_tril,
    )

    return ctx