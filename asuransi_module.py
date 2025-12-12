# asuransi_module.py
import os
import pandas as pd
import logging
from db_loaders import load_asuransi_data_from_db

logger = logging.getLogger(__name__)

DATA_PATH_AS = os.path.join("data", "KINERJA NONBANK.xlsx")
SHEET_NAME_AS = "ASURANSI"   # sesuaikan dengan nama sheet

# -------------------------------------------------
# LOAD & CLEAN DATA
# -------------------------------------------------
def load_asuransi_data():
    """Load asuransi data from database, fallback to Excel if needed"""
    df = None
    try:
        df = load_asuransi_data_from_db()
        if df is None or df.empty:
            # Fallback to Excel
            logger.warning("⚠️  [ASURANSI] Database kosong, menggunakan file Excel sebagai fallback")
            df = pd.read_excel(DATA_PATH_AS, sheet_name=SHEET_NAME_AS)
            logger.info(f"📄 [ASURANSI] Data dimuat dari Excel: {len(df)} baris")
        else:
            # Data from DB needs processing too (column renaming, etc.)
            logger.info(f"✅ [ASURANSI] Data dimuat dari database: {len(df)} baris")
    except Exception as e:
        logger.error(f"❌ [ASURANSI] Error loading from DB: {e}, falling back to Excel")
        try:
            df = pd.read_excel(DATA_PATH_AS, sheet_name=SHEET_NAME_AS)
            logger.info(f"📄 [ASURANSI] Data dimuat dari Excel (fallback): {len(df)} baris")
        except Exception as excel_error:
            logger.error(f"❌ [ASURANSI] Error loading from Excel: {excel_error}")
            raise ValueError(f"Tidak dapat memuat data Asuransi dari database maupun Excel: {excel_error}")
    
    if df is None or df.empty:
        raise ValueError("Data Asuransi tidak dapat dimuat atau kosong")
    
    # Process both database and Excel data
    df.columns = df.columns.astype(str).str.strip()

    # Standarisasi nama kolom (handle both database and Excel column names)
    rename_map = {
        "Premi (Rp Juta)": "Premi",
        "Klaim (Rp Juta)": "Klaim",
        "Jumlah Peserta Premi": "Peserta Premi",
        "Jumlah Peserta Klaim": "Peserta Klaim",
        "Jumlah Peserta Klaim ": "Peserta Klaim",  # Handle trailing space from DB
        "Jumlah Polis Premi": "Polis Premi",
        "Jumlah Polis Klaim": "Polis Klaim",
        "Jumlah Polis Klaim ": "Polis Klaim",  # Handle trailing space from DB
    }
    # Only rename columns that exist
    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Tahun → int
    df["Tahun"] = df["Tahun"].astype(int)

    # Mapping Periode → quarter (1–4) untuk urutan & tanggal
    def parse_quarter(x):
        s = str(x).strip().lower()
        mapping = {
            "triwulan i": 1,
            "triwulan 1": 1,
            "triwulan ii": 2,
            "triwulan 2": 2,
            "triwulan iii": 3,
            "triwulan 3": 3,
            "triwulan iv": 4,
            "triwulan 4": 4,
        }
        return mapping.get(s, 1)

    df["Quarter"] = df["Periode"].apply(parse_quarter).astype(int)

    # Helper: angka Indonesia → float
    def clean_num(s):
        return (
            s.astype(str)
             .str.strip()
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)
             .str.replace(",", ".", regex=False)
        )

    # Premi & Klaim (Rp Juta) → float
    for col in ["Premi", "Klaim"]:
        if df[col].dtype == object:
            df[col] = clean_num(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Peserta & Polis → integer
    for col in ["Peserta Premi", "Peserta Klaim", "Polis Premi", "Polis Klaim"]:
        if col in df.columns:
            if df[col].dtype == object:
                # format seperti 394,00 → 394
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(" ", "", regex=False)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            df[col] = df[col].round(0).astype(int)

    # Tanggal representatif per quarter (pakai bulan ke-3 tiap triwulan: Mar, Jun, Sep, Des)
    df["periode_dt"] = pd.to_datetime(
        dict(year=df["Tahun"], month=df["Quarter"] * 3, day=1)
    )

    return df

# -------------------------------------------------
# HELPER
# -------------------------------------------------
def growth_class(v):
    if v is None or abs(v) < 1e-9:
        return "secondary"
    return "success" if v >= 0 else "danger"


def compute_growth(agg, metric, selected_year, selected_quarter):
    """
    Growth sederhana berbasis quarter (Premi, Klaim, dll).
    Dipakai kalau kamu butuh YoY/YtD. Tidak wajib untuk loss ratio.
    """
    if agg.empty:
        return 0.0, None, None

    agg = agg.sort_values("periode_dt")
    current = None

    if selected_year is not None:
        year_df = agg[agg["Tahun"] == selected_year].sort_values("periode_dt")
        if selected_quarter is not None:
            yq = year_df[year_df["Quarter"] == selected_quarter]
            if not yq.empty:
                current = yq.iloc[-1]
            else:
                le = year_df[year_df["Quarter"] <= selected_quarter]
                if not le.empty:
                    current = le.iloc[-1]
        else:
            if not year_df.empty:
                current = year_df.iloc[-1]

    if current is None:
        current = agg.iloc[-1]

    curr_year = int(current["Tahun"])
    curr_quarter = int(current["Quarter"])
    curr_val = float(current[metric]) if pd.notna(current[metric]) else 0.0

    # YoY: bandingkan quarter yang sama tahun sebelumnya
    yoy = None
    prev_yoy = agg[(agg["Tahun"] == curr_year - 1) & (agg["Quarter"] == curr_quarter)]
    if not prev_yoy.empty:
        prev_val = float(prev_yoy.iloc[0][metric])
        if prev_val != 0:
            yoy = (curr_val - prev_val) / prev_val * 100.0

    # YtD: bandingkan dengan quarter pertama di tahun yang sama
    ytd = None
    same_year = agg[agg["Tahun"] == curr_year].sort_values("periode_dt")
    if not same_year.empty:
        first_row = same_year.iloc[0]
        prev_val = float(first_row[metric])
        if prev_val != 0:
            ytd = (curr_val - prev_val) / prev_val * 100.0

    return curr_val, yoy, ytd


# -------------------------------------------------
# BUILD CONTEXT UNTUK TEMPLATE
# -------------------------------------------------
def build_asuransi_context(request):
    df = load_asuransi_data()

    # Dropdown list
    provinsi_list = sorted(df["Provinsi"].dropna().unique().tolist())
    kabupaten_list = sorted(df["Kabupaten"].dropna().unique().tolist())
    jenis_list = sorted(df["Jenis"].dropna().unique().tolist())
    tahun_list = sorted(df["Tahun"].dropna().unique().tolist())

    # Periode label (Triwulan I, II, ...) pakai urutan Quarter
    periode_order = (
        df[["Periode", "Quarter"]]
        .drop_duplicates()
        .sort_values("Quarter")
    )
    periode_list = periode_order["Periode"].tolist()

    # Ambil filter dari query string
    provinsi = request.args.get("provinsi") or ""
    kabupaten = request.args.get("kabupaten") or ""
    jenis = request.args.get("jenis") or ""
    tahun = request.args.get("tahun") or ""
    periode = request.args.get("periode") or ""  # isi: "Triwulan I", dst

    selected_year = int(tahun) if tahun else None
    selected_quarter = None
    if periode:
        # map ulang ke quarter, sama dengan yang di load_asuransi_data
        selected_quarter = df.loc[df["Periode"] == periode, "Quarter"]
        selected_quarter = int(selected_quarter.iloc[0]) if not selected_quarter.empty else None

    # Filter wilayah & jenis
    df_region = df.copy()
    if provinsi:
        df_region = df_region[df_region["Provinsi"] == provinsi]
    if kabupaten:
        df_region = df_region[df_region["Kabupaten"] == kabupaten]
    if jenis:
        df_region = df_region[df_region["Jenis"] == jenis]

    if df_region.empty:
        df_region = df.copy()

    # Data untuk KPI & rasio (mengikuti filter tahun/periode kalau ada)
    df_filtered = df_region.copy()
    if selected_year is not None:
        df_filtered = df_filtered[df_filtered["Tahun"] == selected_year]
    if periode:
        df_filtered = df_filtered[df_filtered["Periode"] == periode]

    # Kalau setelah filter kosong, fallback ke df_region (supaya nggak 0 terus)
    if df_filtered.empty:
        df_filtered = df_region.copy()

    # ---------------- KPI utama: Premi, Klaim, Loss Ratio (Nominal) ----------------
    as_premi_total = df_filtered["Premi"].sum()
    as_klaim_total = df_filtered["Klaim"].sum()

    as_loss_ratio_klaim = 0.0
    if as_premi_total > 0:
        as_loss_ratio_klaim = as_klaim_total / as_premi_total * 100.0

    # ---------------- KPI Peserta / Polis ----------------
    as_peserta_premi = df_filtered["Peserta Premi"].sum()
    as_peserta_klaim = df_filtered["Peserta Klaim"].sum()
    as_polis_premi = df_filtered["Polis Premi"].sum()
    as_polis_klaim = df_filtered["Polis Klaim"].sum()

    # INI YANG KAMU MAKSUD: LOSS RATIO BERDASARKAN PESERTA PREMI
    as_loss_ratio_peserta = 0.0
    if as_peserta_premi > 0:
        as_loss_ratio_peserta = as_peserta_klaim / as_peserta_premi * 100.0

    # ---------------- Aggregasi quarter untuk chart tren ----------------
    agg_quarter = (
        df_region
        .groupby(["Tahun", "Quarter"], as_index=False)
        .agg({
            "Premi": "sum",
            "Klaim": "sum",
            "Peserta Premi": "sum",
            "Peserta Klaim": "sum",
        })
    )
    agg_quarter["periode_dt"] = pd.to_datetime(
        dict(year=agg_quarter["Tahun"], month=agg_quarter["Quarter"] * 3, day=1)
    )
    agg_quarter = agg_quarter.sort_values("periode_dt")

    # Label timeline: misal "Triw I '24"
    label_map = {1: "Triw I", 2: "Triw II", 3: "Triw III", 4: "Triw IV"}
    as_trend_labels = [
        f"{label_map.get(q, f'Triw {q}')} '{str(y)[-2:]}"
        for y, q in zip(agg_quarter["Tahun"], agg_quarter["Quarter"])
    ]
    as_trend_premi = agg_quarter["Premi"].tolist()
    as_trend_klaim = agg_quarter["Klaim"].tolist()

    # Loss ratio klaim per quarter (Klaim/Premi)
    lr_series = []
    for p, k in zip(as_trend_premi, as_trend_klaim):
        if p > 0:
            lr_series.append(k / p * 100.0)
        else:
            lr_series.append(0.0)

    # ---------------- Share Premi per Jenis (Pie) ----------------
    share_base = df_filtered.copy()
    share_jenis = (
        share_base.groupby("Jenis", as_index=False)["Premi"].sum()
    ).sort_values("Premi", ascending=False)

    as_share_labels = share_jenis["Jenis"].tolist()
    as_share_values = share_jenis["Premi"].tolist()

    # ---------------- Context untuk template ----------------
    ctx = dict(
        provinsi_list=provinsi_list,
        kabupaten_list=kabupaten_list,
        jenis_list=jenis_list,
        tahun_list=tahun_list,
        periode_list=periode_list,
        provinsi_selected=provinsi,
        kabupaten_selected=kabupaten,
        jenis_selected=jenis,
        tahun_selected=tahun,
        periode_selected=periode,

        # KPI nominal
        as_premi_total=as_premi_total,
        as_klaim_total=as_klaim_total,
        as_loss_ratio_klaim=as_loss_ratio_klaim,

        # KPI peserta/polis
        as_peserta_premi=as_peserta_premi,
        as_peserta_klaim=as_peserta_klaim,
        as_polis_premi=as_polis_premi,
        as_polis_klaim=as_polis_klaim,
        as_loss_ratio_peserta=as_loss_ratio_peserta,

        # Tren Premi & Klaim (quarter)
        as_trend_labels=as_trend_labels,
        as_trend_premi=as_trend_premi,
        as_trend_klaim=as_trend_klaim,
        as_trend_lossratio=lr_series,

        # Pie share premi per jenis
        as_share_labels=as_share_labels,
        as_share_values=as_share_values,
    )

    return ctx
