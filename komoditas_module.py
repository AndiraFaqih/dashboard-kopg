# komoditas_module.py
import os
import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# ==========================================
# KONFIGURASI DATA KOMODITAS
# ==========================================
DATA_PATH_KOM = os.path.join("data", "Komoditas.xlsx")
SHEET_NAME_KOM = "raw-all-komoditas"


# ==========================================
# KOMODITAS
# ==========================================
def load_komoditas_data():
    """
    Mengubah tabel komoditas lebar (multi header 3 baris:
    Klasifikasi | Tahun | Komoditas) menjadi format long:

        Provinsi | Tahun | Klasifikasi | Komoditas | Satuan | Nilai
    """
    df_raw = pd.read_excel(
        DATA_PATH_KOM,
        sheet_name=SHEET_NAME_KOM,
        header=[0, 1, 2],   # 3 baris header
    )

    # Cari kolom provinsi (header level terakhir = "Komoditas")
    prov_col = None
    for c in df_raw.columns:
        last = c[-1] if isinstance(c, tuple) else c
        if str(last).strip().lower() == "komoditas":
            prov_col = c
            break
    if prov_col is None:
        prov_col = df_raw.columns[0]

    id_col = prov_col
    value_cols = [c for c in df_raw.columns if c != id_col]

    df_long = df_raw.melt(
        id_vars=[id_col],
        value_vars=value_cols,
        var_name=["Klasifikasi", "Tahun", "KomoditasRaw"],
        value_name="NilaiRaw",
    )

    df_long = df_long.rename(columns={id_col: "Provinsi"})

    # Provinsi
    df_long["Provinsi"] = df_long["Provinsi"].astype(str).str.strip()

    # Klasifikasi
    df_long["Klasifikasi"] = df_long["Klasifikasi"].astype(str).str.strip()

    # Tahun → 4 digit → int
    df_long["Tahun"] = (
        df_long["Tahun"]
        .astype(str)
        .str.extract(r"(\d{4})", expand=False)
    )
    df_long["Tahun"] = pd.to_numeric(df_long["Tahun"], errors="coerce")

    # Komoditas + satuan: "Padi (Ton)" → ("Padi", "Ton")
    def split_komoditas(s):
        s = str(s).strip()
        m = re.match(r"(.+?)\s*\((.+?)\)\s*$", s)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        else:
            return s, None

    kom_satuan = df_long["KomoditasRaw"].apply(split_komoditas)
    df_long["Komoditas"] = kom_satuan.apply(lambda x: x[0])
    df_long["Satuan"] = kom_satuan.apply(lambda x: x[1])

    # Nilai angka Indonesia → float
    df_long["Nilai"] = (
        df_long["NilaiRaw"]
        .astype(str)
        .str.strip()
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)   # ribuan
        .str.replace(",", ".", regex=False)  # desimal
    )
    df_long["Nilai"] = pd.to_numeric(df_long["Nilai"], errors="coerce").fillna(0.0)

    # Bersihkan provinsi kosong
    df_long["Provinsi"] = df_long["Provinsi"].astype(str).str.strip()
    df_long = df_long[
        (df_long["Provinsi"] != "") &
        (~df_long["Provinsi"].str.lower().isin(["nan", "none"])) &
        df_long["Provinsi"].notna()
    ]

    # Buang tahun NaN, paksa ke int
    df_long = df_long[df_long["Tahun"].notna()]
    df_long["Tahun"] = df_long["Tahun"].astype(int)

    logger.info(
        f"📄 [KOMODITAS] Data dimuat dari Excel: {len(df_long)} baris | "
        f"provinsi unik: {df_long['Provinsi'].nunique()} | "
        f"tahun unik: {sorted(df_long['Tahun'].unique())} | "
        f"klasifikasi unik: {df_long['Klasifikasi'].unique()}"
    )

    return df_long

# --- DATA KOMODITAS KAB/KOTA (KOPI) ---
# SESUAIKAN nama file & sheet dengan file kamu
DATA_PATH_KOM_KAB = os.path.join("data", "Data Komoditi (1).xlsx")
SHEET_NAME_KOM_KAB = "Sheet1"

def load_komoditas_kabkota_data():
    """
    Data bentuk:

    Komoditi | Provinsi | Kabupaten/Kota | Produksi (Ton) | Luas Lahan (Ha)

    Contoh:
    Kopi | Sumatera Selatan | Ogan Komering Ulu  | 16.355 | 22.099
    Kopi | Sumatera Selatan | Ogan Komering Ilir |   340  |   814
    Kopi | Sumatera Selatan | Muara Enim         | 28.650 | 22.475
    """
    df = pd.read_excel(
        DATA_PATH_KOM_KAB,
        sheet_name=SHEET_NAME_KOM_KAB,
    )

    df = df.rename(columns={
        "Komoditi": "Komoditas",
        "Kabupaten/Kota": "KabKota",
        "Produksi (Ton)": "Produksi",
        "Luas Lahan (Ha)": "LuasLahan",
    })

    print(df)

    # Bersihkan teks  ✅ pakai .str.strip()
    for col in ["Komoditas", "Provinsi", "KabKota"]:
        df[col] = df[col].astype(str).str.strip()

    # Angka Indonesia -> float
    for col in ["Produksi", "LuasLahan"]:
        series = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)   # ribuan
            .str.replace(",", ".", regex=False)  # desimal
        )
        df[col] = pd.to_numeric(series, errors="coerce").fillna(0.0)

    return df



def build_komoditas_context(request):
    df = load_komoditas_data()

    # --------------------------
    # DROPDOWN OPTIONS DASAR
    # --------------------------
    provinsi_list = sorted(df["Provinsi"].dropna().unique().tolist())

    tahun_list = (
        df["Tahun"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
        .tolist()
    )

    klasifikasi_list = sorted(
        df["Klasifikasi"].dropna().astype(str).unique().tolist()
    )

    # --------------------------
    # AMBIL FILTER DARI QUERY
    # --------------------------
    provinsi = (request.args.get("provinsi") or "").strip()

    tahun_raw = request.args.get("tahun")         # None kalau pertama kali load
    tahun_param = (tahun_raw or "").strip()

    klas_raw = request.args.get("klasifikasi")
    klasifikasi_param = (klas_raw or "").strip()

    komoditas_param = (request.args.get("komoditas") or "").strip()

    # Filter jumlah petani
    petani_provinsi_param = (request.args.get("petani_provinsi") or "").strip()
    petani_kabkota_param = (request.args.get("petani_kabkota") or "").strip()

    # --------------------------
    # TAHUN TERPILIH
    # - pertama kali buka → tahun terbaru
    # - kalau user pilih "Semua" → selected_year = None
    # --------------------------
    if tahun_raw is None:
        selected_year = int(tahun_list[-1]) if tahun_list else None
    else:
        if tahun_param:
            try:
                selected_year = int(tahun_param)
            except ValueError:
                selected_year = None
        else:
            # user pilih "Semua"
            selected_year = None

    # --------------------------
    # KLASIFIKASI TERPILIH
    # - pertama kali buka → Tanaman Pangan (kalau ada)
    # - kalau pilih "Semua" → selected_klas = ""
    # --------------------------
    if klas_raw is None:
        if "Tanaman Pangan" in klasifikasi_list:
            selected_klas = "Tanaman Pangan"
        else:
            selected_klas = klasifikasi_list[0] if klasifikasi_list else ""
    else:
        selected_klas = klasifikasi_param  # "" artinya semua klasifikasi

    # --------------------------
    # DROPDOWN KOMODITAS
    #   tergantung Tahun + Klasifikasi
    # --------------------------
    df_for_kom_opts = df.copy()
    if selected_year is not None:
        df_for_kom_opts = df_for_kom_opts[df_for_kom_opts["Tahun"] == selected_year]
    if selected_klas:
        df_for_kom_opts = df_for_kom_opts[df_for_kom_opts["Klasifikasi"] == selected_klas]

    komoditas_list = sorted(
        df_for_kom_opts["Komoditas"].dropna().astype(str).unique().tolist()
    )

    if komoditas_param and komoditas_param in komoditas_list:
        selected_komoditas = komoditas_param
    else:
        selected_komoditas = ""   # "Semua"

    # --------------------------
    # FILTER DATA KPI
    #   (Tahun + Klasifikasi + Komoditas + Provinsi)
    # --------------------------
    df_filtered = df.copy()
    if selected_year is not None:
        df_filtered = df_filtered[df_filtered["Tahun"] == selected_year]
    if selected_klas:
        df_filtered = df_filtered[df_filtered["Klasifikasi"] == selected_klas]
    if selected_komoditas:
        df_filtered = df_filtered[df_filtered["Komoditas"] == selected_komoditas]
    if provinsi:
        df_filtered = df_filtered[df_filtered["Provinsi"] == provinsi]

    # Nilai default
    unit_label = ""
    total_val = 0.0
    komoditas_count = 0
    top_kom_name = ""
    top_kom_val = 0.0
    top_kom_share = 0.0

    if not df_filtered.empty:
        # satuan
        unit_list = df_filtered["Satuan"].dropna().unique().tolist()
        unit_label = unit_list[0] if unit_list else ""

        # total produksi
        total_val = float(df_filtered["Nilai"].sum())

        # agregasi per komoditas (untuk KPI)
        df_by_kom_kpi = (
            df_filtered
            .groupby("Komoditas", as_index=False)["Nilai"]
            .sum()
            .sort_values("Nilai", ascending=False)
        )
        komoditas_count = df_by_kom_kpi.shape[0]

        if not df_by_kom_kpi.empty:
            top_kom_name = df_by_kom_kpi.iloc[0]["Komoditas"]
            top_kom_val = float(df_by_kom_kpi.iloc[0]["Nilai"])
            top_kom_share = (top_kom_val / total_val * 100.0) if total_val > 0 else 0.0

    # --------------------------
    # CHART: TOP 10 KOMODITAS
    #   HANYA ikut Tahun + Klasifikasi + Provinsi
    #   (TIDAK ikut filter komoditas)
    # --------------------------
    df_for_kom_chart = df.copy()
    if selected_year is not None:
        df_for_kom_chart = df_for_kom_chart[df_for_kom_chart["Tahun"] == selected_year]
    if selected_klas:
        df_for_kom_chart = df_for_kom_chart[df_for_kom_chart["Klasifikasi"] == selected_klas]
    if provinsi:
        df_for_kom_chart = df_for_kom_chart[df_for_kom_chart["Provinsi"] == provinsi]

    kom_kom_labels = []
    kom_kom_values = []

    if not df_for_kom_chart.empty:
        df_by_kom_chart = (
            df_for_kom_chart
            .groupby("Komoditas", as_index=False)["Nilai"]
            .sum()
            .sort_values("Nilai", ascending=False)
        )
        df_top10 = df_by_kom_chart.head(10)
        kom_kom_labels = df_top10["Komoditas"].tolist()
        kom_kom_values = df_top10["Nilai"].round(2).tolist()

    # --------------------------
    # CHART: TOP 10 PROVINSI
    #   Ikut Tahun + Klasifikasi + (opsional Komoditas)
    # --------------------------
    if selected_year is not None and selected_klas:
        df_for_prov = df[
            (df["Tahun"] == selected_year) &
            (df["Klasifikasi"] == selected_klas)
        ]
    else:
        df_for_prov = df.copy()

    if selected_komoditas:
        df_for_prov = df_for_prov[df_for_prov["Komoditas"] == selected_komoditas]

    kom_prov_labels = []
    kom_prov_values = []
    top_prov_name = ""
    top_prov_val = 0.0

    if not df_for_prov.empty:
        df_by_prov = (
            df_for_prov
            .groupby("Provinsi", as_index=False)["Nilai"]
            .sum()
            .sort_values("Nilai", ascending=False)
        )
        df_top_prov = df_by_prov.head(10)
        kom_prov_labels = df_top_prov["Provinsi"].tolist()
        kom_prov_values = df_top_prov["Nilai"].round(2).tolist()

        if not df_by_prov.empty:
            top_prov_name = df_by_prov.iloc[0]["Provinsi"]
            top_prov_val = float(df_by_prov.iloc[0]["Nilai"])

    # =====================================================
    #  DETAIL KOMODITAS PER KAB/KOTA (contoh: Kopi)
    # =====================================================
    # =====================================================
    #  DETAIL KOMODITAS PER KAB/KOTA (contoh: Kopi)
    # =====================================================
    try:
        df_kab = load_komoditas_kabkota_data()
    except Exception as e:
        print("[KOM-KAB] ERROR load:", e)
        df_kab = pd.DataFrame(columns=["Komoditas", "Provinsi", "KabKota", "Produksi", "LuasLahan"])

    df_kab_filtered = df_kab.copy()

    # Filter ikut komoditas & provinsi yang sedang dipilih di dashboard
    if selected_komoditas:
        df_kab_filtered = df_kab_filtered[
            df_kab_filtered["Komoditas"].str.lower() == selected_komoditas.lower()
        ]
    if provinsi:
        df_kab_filtered = df_kab_filtered[
            df_kab_filtered["Provinsi"].str.lower() == provinsi.lower()
        ]

    # ---- KPI utama & data chart ----
    if not df_kab_filtered.empty:
        total_produksi = float(df_kab_filtered["Produksi"].sum())
        total_luas = float(df_kab_filtered["LuasLahan"].sum())
        rata_prod_per_ha = (total_produksi / total_luas) if total_luas > 0 else 0.0

        # Kab/Kota dengan produksi tertinggi (untuk kartu KPI)
        df_sorted_prod = df_kab_filtered.sort_values("Produksi", ascending=False)
        kab_top_prod = df_sorted_prod.iloc[0]["KabKota"]
        kab_top_prod_val = float(df_sorted_prod.iloc[0]["Produksi"])

        # Hitung produktivitas (Ton/Ha) per Kab/Kota, hindari divide-by-zero
        luas_nonzero = df_kab_filtered["LuasLahan"].copy()
        luas_nonzero = luas_nonzero.mask(luas_nonzero == 0)
        prod_per_ha = (df_kab_filtered["Produksi"] / luas_nonzero).fillna(0.0)

        # Kab/Kota dengan produktivitas tertinggi (untuk KPI)
        df_tmp = df_kab_filtered.copy()
        df_tmp["ProdPerHa"] = prod_per_ha
        df_sorted_prodperha = df_tmp.sort_values("ProdPerHa", ascending=False)
        kab_top_prodperha = df_sorted_prodperha.iloc[0]["KabKota"]
        kab_top_prodperha_val = float(df_sorted_prodperha.iloc[0]["ProdPerHa"])

        # ---- Top 5 untuk tiap chart ----
        # 1) Top 5 produksi
        df_top_prod = df_sorted_prod.head(5)
        kab_prod_top_labels = df_top_prod["KabKota"].tolist()
        kab_prod_top_values = df_top_prod["Produksi"].round(2).tolist()

        # 2) Top 5 luas lahan
        df_sorted_luas = df_kab_filtered.sort_values("LuasLahan", ascending=False)
        df_top_luas = df_sorted_luas.head(5)
        kab_luas_top_labels = df_top_luas["KabKota"].tolist()
        kab_luas_top_values = df_top_luas["LuasLahan"].round(2).tolist()

        # 3) Top 5 produktivitas (Ton/Ha)
        df_top_prodperha = df_sorted_prodperha.head(5)
        kab_prodperha_top_labels = df_top_prodperha["KabKota"].tolist()
        kab_prodperha_top_values = df_top_prodperha["ProdPerHa"].round(3).tolist()
    else:
        total_produksi = 0.0
        total_luas = 0.0
        rata_prod_per_ha = 0.0
        kab_top_prod = ""
        kab_top_prod_val = 0.0
        kab_top_prodperha = ""
        kab_top_prodperha_val = 0.0
        kab_prod_top_labels = []
        kab_prod_top_values = []
        kab_luas_top_labels = []
        kab_luas_top_values = []
        kab_prodperha_top_labels = []
        kab_prodperha_top_values = []

    # =====================================================
    #  DATA JUMLAH PETANI
    # =====================================================
    try:
        from db_loaders import load_jumlah_petani_data_from_db
        df_petani = load_jumlah_petani_data_from_db()
    except Exception as e:
        logger.warning(f"[JUMLAH PETANI] Error load: {e}")
        df_petani = pd.DataFrame(columns=["Komoditi", "Provinsi", "KabKota", "JumlahPetani"])

    # Dropdown options untuk filter jumlah petani
    petani_provinsi_list = []
    petani_kabkota_list = []
    
    if not df_petani.empty:
        petani_provinsi_list = sorted(df_petani["Provinsi"].dropna().unique().tolist())
        petani_kabkota_list = sorted(df_petani["KabKota"].dropna().unique().tolist())

    # Filter data jumlah petani berdasarkan filter yang dipilih
    df_petani_filtered = df_petani.copy()
    
    if petani_provinsi_param:
        df_petani_filtered = df_petani_filtered[
            df_petani_filtered["Provinsi"].str.strip().str.lower() == petani_provinsi_param.lower()
        ]
    
    if petani_kabkota_param:
        df_petani_filtered = df_petani_filtered[
            df_petani_filtered["KabKota"].str.strip().str.lower() == petani_kabkota_param.lower()
        ]

    # Proses data jumlah petani untuk chart
    petani_labels = []
    petani_values = []
    
    if not df_petani_filtered.empty:
        # Sort by jumlah petani descending dan ambil top entries
        df_petani_sorted = df_petani_filtered.sort_values("JumlahPetani", ascending=False)
        # Ambil top 10 atau semua jika kurang dari 10
        df_petani_top = df_petani_sorted.head(10)
        
        # Format label: Kabupaten/Kota
        petani_labels = df_petani_top["KabKota"].astype(str).str.strip().tolist()
        petani_values = df_petani_top["JumlahPetani"].astype(int).tolist()

    # --------------------------
    # SUSUN CONTEXT
    # --------------------------
    ctx = dict(
        # Dropdown list
        provinsi_list=provinsi_list,
        tahun_list=tahun_list,
        klasifikasi_list=klasifikasi_list,
        komoditas_list=komoditas_list,

        # Selected
        provinsi_selected=provinsi,
        tahun_selected=str(selected_year) if selected_year is not None else "",
        klasifikasi_selected=selected_klas,
        komoditas_selected=selected_komoditas,

        # KPI
        kom_unit_label=unit_label,
        kom_total_val=total_val,
        kom_komoditas_count=komoditas_count,
        kom_top_komoditas=top_kom_name,
        kom_top_komoditas_val=top_kom_val,
        kom_top_komoditas_share=top_kom_share,
        kom_top_provinsi=top_prov_name,
        kom_top_provinsi_val=top_prov_val,

        # Chart data
        kom_kom_labels=kom_kom_labels,
        kom_kom_values=kom_kom_values,
        kom_prov_labels=kom_prov_labels,
        kom_prov_values=kom_prov_values,

        # --- Detail Kab/Kota ---
        kab_total_produksi=total_produksi,
        kab_total_luas=total_luas,
        kab_rata_prod_per_ha=rata_prod_per_ha,
        kab_top_prod_kab=kab_top_prod,
        kab_top_prod_val=kab_top_prod_val,
        kab_top_prodperha_kab=kab_top_prodperha,
        kab_top_prodperha_val=kab_top_prodperha_val,
        kab_prod_top_labels=kab_prod_top_labels,
        kab_prod_top_values=kab_prod_top_values,
        kab_luas_top_labels=kab_luas_top_labels,
        kab_luas_top_values=kab_luas_top_values,
        kab_prodperha_top_labels=kab_prodperha_top_labels,
        kab_prodperha_top_values=kab_prodperha_top_values,

        # --- Jumlah Petani ---
        petani_provinsi_list=petani_provinsi_list,
        petani_kabkota_list=petani_kabkota_list,
        petani_provinsi_selected=petani_provinsi_param,
        petani_kabkota_selected=petani_kabkota_param,
        petani_labels=petani_labels,
        petani_values=petani_values,

    )
    return ctx


# =====================================================
#  KREDIT BERDASARKAN LOKASI  (DIGABUNG DI FILE INI)
# =====================================================

# =====================================================
#  KREDIT BERDASARKAN LOKASI  (DIGABUNG DI FILE INI)
# =====================================================

DATA_PATH_KRL = os.path.join("data", "Kredit Lok Bank - Sub Sektor.xlsx")
SHEET_NAME_KRL = "Page1_1"


def load_kredit_lokasi_data():
    """
    Load kredit lokasi data from database, fallback to Excel if needed.
    """
    from db_loaders import load_kredit_lokasi_data_from_db
    
    try:
        df_long, krl_tahun, krl_jumlah_bulan = load_kredit_lokasi_data_from_db()
        if df_long is None or df_long.empty:
            # Fallback to Excel
            logger.warning("⚠️  [KREDIT LOKASI] Database kosong, menggunakan file Excel sebagai fallback")
            result = load_kredit_lokasi_data_from_excel()
            logger.info(f"📄 [KREDIT LOKASI] Data dimuat dari Excel: {len(result[0])} baris")
            return result
        else:
            logger.info(
                f"✅ [KREDIT LOKASI] Data dimuat dari database: {len(df_long)} baris | "
                f"sektor unik: {df_long['Sektor'].nunique()} | "
                f"lokasi unik: {df_long['Lokasi'].nunique()} | "
                f"tahun: {krl_tahun} | bulan: {krl_jumlah_bulan}"
            )
            return df_long, krl_tahun, krl_jumlah_bulan
    except Exception as e:
        logger.error(f"❌ [KREDIT LOKASI] Error loading from DB: {e}, falling back to Excel")
        result = load_kredit_lokasi_data_from_excel()
        logger.info(f"📄 [KREDIT LOKASI] Data dimuat dari Excel (fallback): {len(result[0])} baris")
        return result


def load_kredit_lokasi_data_from_excel():
    """
    Fallback function to load kredit lokasi from Excel (original implementation).
    """
    # ---- Metadata (jumlah bulan & tahun) ----
    meta = pd.read_excel(
        DATA_PATH_KRL,
        sheet_name=SHEET_NAME_KRL,
        header=None,
        nrows=4
    )
    krl_jumlah_bulan = None
    krl_tahun = None
    try:
        krl_jumlah_bulan = int(pd.to_numeric(meta.iloc[0, 1], errors="coerce"))
    except Exception:
        pass
    try:
        krl_tahun = int(pd.to_numeric(meta.iloc[1, 1], errors="coerce"))
    except Exception:
        # fallback: cari 4 digit tahun di kolom B
        for val in meta.iloc[:, 1].tolist():
            s = str(val)
            m = re.search(r"(\d{4})", s)
            if m:
                krl_tahun = int(m.group(1))
                break

    # ---- Data utama ----
    df_raw = pd.read_excel(
        DATA_PATH_KRL,
        sheet_name=SHEET_NAME_KRL,
        header=3,  # baris ke-4 sebagai header
    )

    # Drop kolom yang kosong semua
    df_raw = df_raw.dropna(axis=1, how="all")

    # Kolom pertama = Sektor
    first_col = df_raw.columns[0]
    df_raw = df_raw.rename(columns={first_col: "Sektor"})
    df_raw["Sektor"] = df_raw["Sektor"].astype(str).str.strip()

    # Buang baris yang tidak dipakai
    lower = df_raw["Sektor"].str.lower()
    is_empty = df_raw["Sektor"].eq("") | lower.eq("nan")
    is_unknown = lower.eq("unknown")
    is_total_lokasi = lower.eq("all")
    is_date = pd.to_datetime(df_raw["Sektor"], errors="coerce").notna()

    df_raw = df_raw[~(is_empty | is_unknown | is_total_lokasi | is_date)].copy()

    # >>> HANYA AMBIL SEKTOR YANG MENGANDUNG KATA "PERKEBUNAN"
    mask_perkebunan = df_raw["Sektor"].str.contains("perkebunan", case=False, na=False)
    df_raw = df_raw[mask_perkebunan].copy()
    # <<<

    # Buang kolom 'All' (total per sektor) – nanti kita hitung sendiri via groupby
    if "All" in df_raw.columns:
        df_raw = df_raw.drop(columns=["All"])

    # Kolom lokasi = semua selain 'Sektor'
    lokasi_cols = [c for c in df_raw.columns if c != "Sektor"]

    # Long format: Sektor | Lokasi | KreditRaw
    df_long = df_raw.melt(
        id_vars=["Sektor"],
        value_vars=lokasi_cols,
        var_name="Lokasi",
        value_name="KreditRaw",
    )

    df_long["Lokasi"] = df_long["Lokasi"].astype(str).str.strip()

    # Angka Indonesia → float
    df_long["Kredit"] = (
        df_long["KreditRaw"]
        .astype(str)
        .str.strip()
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)   # ribuan
        .str.replace(",", ".", regex=False)  # desimal
    )
    df_long["Kredit"] = pd.to_numeric(df_long["Kredit"], errors="coerce").fillna(0.0)

    # Buang baris lokasi kosong
    df_long = df_long[
        (df_long["Lokasi"] != "") &
        df_long["Lokasi"].notna()
    ]

    print(
        "[KRL] rows:", len(df_long),
        "| sektor unik:", df_long["Sektor"].nunique(),
        "| lokasi unik:", df_long["Lokasi"].nunique(),
        "| tahun:", krl_tahun,
        "| bulan:", krl_jumlah_bulan,
    )

    return df_long, krl_tahun, krl_jumlah_bulan


def build_kredit_lokasi_context(request):
    """
    Context untuk bagian dashboard Kredit berdasarkan Lokasi.
    Parameter pakai prefix 'krl_' supaya tidak tabrakan dengan filter komoditas.
    """
    df, krl_tahun, krl_jumlah_bulan = load_kredit_lokasi_data()

    # Dropdown
    sektor_list = sorted(df["Sektor"].dropna().unique().tolist())
    lokasi_list = sorted(df["Lokasi"].dropna().unique().tolist())

    sektor_param = (request.args.get("krl_sektor") or "").strip()
    lokasi_param = (request.args.get("krl_lokasi") or "").strip()

    # ---------- TOTAL KREDIT (FILTER SAAT INI) ----------
    df_filtered = df.copy()
    if sektor_param:
        df_filtered = df_filtered[df_filtered["Sektor"] == sektor_param]
    if lokasi_param:
        df_filtered = df_filtered[df_filtered["Lokasi"] == lokasi_param]

    krl_total_kredit = float(df_filtered["Kredit"].sum()) if not df_filtered.empty else 0.0

    # ---------- TOP LOKASI (respek filter sektor, abaikan filter lokasi) ----------
    if sektor_param:
        df_for_lokasi = df[df["Sektor"] == sektor_param]
    else:
        df_for_lokasi = df.copy()

    df_by_lokasi = (
        df_for_lokasi
        .groupby("Lokasi", as_index=False)["Kredit"]
        .sum()
        .sort_values("Kredit", ascending=False)
    )
    df_top10_lokasi = df_by_lokasi.head(10)

    krl_lokasi_labels = df_top10_lokasi["Lokasi"].tolist()
    krl_lokasi_values = df_top10_lokasi["Kredit"].round(2).tolist()

    if not df_by_lokasi.empty:
        krl_top_lokasi = df_by_lokasi.iloc[0]["Lokasi"]
        krl_top_lokasi_val = float(df_by_lokasi.iloc[0]["Kredit"])
    else:
        krl_top_lokasi = ""
        krl_top_lokasi_val = 0.0

    # ---------- TOP SEKTOR (respek filter lokasi, abaikan filter sektor) ----------
    if lokasi_param:
        df_for_sektor = df[df["Lokasi"] == lokasi_param]
    else:
        df_for_sektor = df.copy()

    df_by_sektor = (
        df_for_sektor
        .groupby("Sektor", as_index=False)["Kredit"]
        .sum()
        .sort_values("Kredit", ascending=False)
    )
    df_top10_sektor = df_by_sektor.head(10)

    krl_sektor_labels = df_top10_sektor["Sektor"].tolist()
    krl_sektor_values = df_top10_sektor["Kredit"].round(2).tolist()

    if not df_by_sektor.empty:
        krl_top_sektor = df_by_sektor.iloc[0]["Sektor"]
        krl_top_sektor_val = float(df_by_sektor.iloc[0]["Kredit"])
    else:
        krl_top_sektor = ""
        krl_top_sektor_val = 0.0

    ctx = dict(
        # dropdown
        krl_sektor_list=sektor_list,
        krl_lokasi_list=lokasi_list,
        krl_sektor_selected=sektor_param,
        krl_lokasi_selected=lokasi_param,

        # metadata
        krl_tahun=krl_tahun,
        krl_jumlah_bulan=krl_jumlah_bulan,

        # KPI
        krl_total_kredit=krl_total_kredit,
        krl_top_lokasi=krl_top_lokasi,
        krl_top_lokasi_val=krl_top_lokasi_val,
        krl_top_sektor=krl_top_sektor,
        krl_top_sektor_val=krl_top_sektor_val,

        # chart data
        krl_lokasi_labels=krl_lokasi_labels,
        krl_lokasi_values=krl_lokasi_values,
        krl_sektor_labels=krl_sektor_labels,
        krl_sektor_values=krl_sektor_values,
    )
    return ctx

