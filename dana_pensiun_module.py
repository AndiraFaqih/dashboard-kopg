# dana_pensiun_module.py
import os
import pandas as pd
import logging
from db_loaders import load_dana_pensiun_data_from_db

logger = logging.getLogger(__name__)

DATA_PATH_DP = os.path.join("data", "KINERJA NONBANK.xlsx")  # sesuaikan
SHEET_NAME_DP = "DANA PENSIUN"  # sesuaikan

def load_dp_data():
    """Load dana pensiun data from database, fallback to Excel if needed"""
    df = None
    try:
        df = load_dana_pensiun_data_from_db()
        if df is None or df.empty:
            # Fallback to Excel
            logger.warning("⚠️  [DANA PENSIUN] Database kosong, menggunakan file Excel sebagai fallback")
            df = pd.read_excel(DATA_PATH_DP, sheet_name=SHEET_NAME_DP)
            logger.info(f"📄 [DANA PENSIUN] Data dimuat dari Excel: {len(df)} baris")
        else:
            # Data from DB needs processing too (column renaming, number cleaning, etc.)
            logger.info(f"✅ [DANA PENSIUN] Data dimuat dari database: {len(df)} baris")
    except Exception as e:
        logger.error(f"❌ [DANA PENSIUN] Error loading from DB: {e}, falling back to Excel")
        try:
            df = pd.read_excel(DATA_PATH_DP, sheet_name=SHEET_NAME_DP)
            logger.info(f"📄 [DANA PENSIUN] Data dimuat dari Excel (fallback): {len(df)} baris")
        except Exception as excel_error:
            logger.error(f"❌ [DANA PENSIUN] Error loading from Excel: {excel_error}")
            raise ValueError(f"Tidak dapat memuat data Dana Pensiun dari database maupun Excel: {excel_error}")
    
    if df is None or df.empty:
        raise ValueError("Data Dana Pensiun tidak dapat dimuat atau kosong")
    df.columns = df.columns.astype(str).str.strip()

    df = df.rename(columns={
        "Aset (Rp Miliar)": "Aset",
        "Aset Neto (Rp Miliar)": "Aset Neto",
        "Investasi (Rp Miliar)": "Investasi",
    })

    def parse_bulan(x):
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

    df["Tahun"] = df["Tahun"].astype(int)
    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)

    def clean_num(s):
        return (
            s.astype(str)
             .str.strip()
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)
             .str.replace(",", ".", regex=False)
        )

    for col in ["Aset", "Aset Neto", "Investasi"]:
        if df[col].dtype == object:
            df[col] = clean_num(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if df["Jumlah Dana Pensiun"].dtype == object:
        df["Jumlah Dana Pensiun"] = (
            df["Jumlah Dana Pensiun"]
            .astype(str)
            .str.strip()
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
        )
    df["Jumlah Dana Pensiun"] = pd.to_numeric(
        df["Jumlah Dana Pensiun"], errors="coerce"
    ).fillna(0).astype(int)

    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df

def make_agg_month_dp(df_src: pd.DataFrame) -> pd.DataFrame:
    agg = df_src.groupby(["Tahun", "Bulan"], as_index=False).agg(
        {
            "Aset": "sum",
            "Aset Neto": "sum",
            "Investasi": "sum",
            "Jumlah Dana Pensiun": "sum",
        }
    )
    agg["periode"] = pd.to_datetime(dict(year=agg["Tahun"], month=agg["Bulan"], day=1))
    return agg

def compute_growth(agg, metric, selected_year, selected_month):
    if agg.empty:
        return 0.0, None, None
    agg = agg.sort_values("periode")
    current = None

    if selected_year is not None:
        year_df = agg[agg["Tahun"] == selected_year].sort_values("periode")
        if selected_month is not None:
            ym = year_df[year_df["Bulan"] == selected_month]
            if not ym.empty:
                current = ym.iloc[-1]
            else:
                le = year_df[year_df["Bulan"] <= selected_month]
                if not le.empty:
                    current = le.iloc[-1]
        else:
            if not year_df.empty:
                current = year_df.iloc[-1]

    if current is None:
        current = agg.iloc[-1]

    curr_year = int(current["Tahun"])
    curr_month = int(current["Bulan"])
    curr_val = float(current[metric]) if pd.notna(current[metric]) else 0.0

    yoy = None
    prev_yoy = agg[(agg["Tahun"] == curr_year - 1) & (agg["Bulan"] == curr_month)]
    if not prev_yoy.empty:
        prev_val = float(prev_yoy.iloc[0][metric])
        if prev_val != 0:
            yoy = (curr_val - prev_val) / prev_val * 100.0

    ytd = None
    same_year = agg[agg["Tahun"] == curr_year].sort_values("periode")
    if not same_year.empty:
        first_row = same_year.iloc[0]
        prev_val = float(first_row[metric])
        if prev_val != 0:
            ytd = (curr_val - prev_val) / prev_val * 100.0

    return curr_val, yoy, ytd

def growth_class(v):
    if v is None or abs(v) < 1e-9:
        return "secondary"
    return "success" if v >= 0 else "danger"

def build_dana_pensiun_context(request):
    df = load_dp_data()

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

    df_region = df.copy()
    if negara:
        df_region = df_region[df_region["Negara"] == negara]
    if provinsi:
        df_region = df_region[df_region["Provinsi"] == provinsi]
    if df_region.empty:
        df_region = df.copy()

    agg_month = make_agg_month_dp(df_region)

    dp_aset_val, dp_aset_yoy, dp_aset_ytd = compute_growth(
        agg_month, "Aset", selected_year, selected_month
    )
    dp_asetnet_val, dp_asetnet_yoy, dp_asetnet_ytd = compute_growth(
        agg_month, "Aset Neto", selected_year, selected_month
    )
    dp_invest_val, dp_invest_yoy, dp_invest_ytd = compute_growth(
        agg_month, "Investasi", selected_year, selected_month
    )
    dp_jumlah_val, dp_jumlah_yoy, dp_jumlah_ytd = compute_growth(
        agg_month, "Jumlah Dana Pensiun", selected_year, selected_month
    )

    agg_year = (
        agg_month.groupby(["Tahun"], as_index=False)
        .agg(
            {
                "Aset": "sum",
                "Aset Neto": "sum",
                "Investasi": "sum",
                "Jumlah Dana Pensiun": "sum",
            }
        )
        .sort_values("Tahun")
    )
    dp_year_labels  = agg_year["Tahun"].astype(str).tolist()
    dp_year_aset    = agg_year["Aset"].tolist()
    dp_year_asetnet = agg_year["Aset Neto"].tolist()
    dp_year_invest  = agg_year["Investasi"].tolist()
    dp_year_jumlah  = agg_year["Jumlah Dana Pensiun"].tolist()

    # mini 3 periode (boleh simple aja: pakai bulanan)
    base_labels = agg_month["periode"].dt.strftime("%b '%y").tolist()
    base_aset   = agg_month["Aset"].tolist()
    base_invest = agg_month["Investasi"].tolist()
    base_jumlah = agg_month["Jumlah Dana Pensiun"].tolist()

    if len(base_labels) >= 3:
        dp_mini_labels = base_labels[-3:]
        dp_mini_aset   = base_aset[-3:]
        dp_mini_invest = base_invest[-3:]
        dp_mini_jumlah = base_jumlah[-3:]
    else:
        dp_mini_labels = base_labels
        dp_mini_aset   = base_aset
        dp_mini_invest = base_invest
        dp_mini_jumlah = base_jumlah

    # rasio Desember (optional, bisa dikosongkan kalau belum mau dipakai)
    dec_all = agg_month[agg_month["Bulan"] == 12].sort_values("Tahun")
    dp_ratio_labels = [f"Des'{str(y)[-2:]}" for y in dec_all["Tahun"]]
    aset = dec_all["Aset"].replace(0, pd.NA)
    invest = dec_all["Investasi"]
    asetnet = dec_all["Aset Neto"]

    dp_ratio_invest = ((invest / aset) * 100).fillna(0).tolist()
    dp_ratio_asetnet = ((asetnet / aset) * 100).fillna(0).tolist()

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
        dp_aset_val=dp_aset_val,
        dp_aset_yoy=dp_aset_yoy,
        dp_aset_ytd=dp_aset_ytd,
        dp_aset_yoy_class=growth_class(dp_aset_yoy),
        dp_aset_ytd_class=growth_class(dp_aset_ytd),
        dp_asetnet_val=dp_asetnet_val,
        dp_asetnet_yoy=dp_asetnet_yoy,
        dp_asetnet_ytd=dp_asetnet_ytd,
        dp_asetnet_yoy_class=growth_class(dp_asetnet_yoy),
        dp_asetnet_ytd_class=growth_class(dp_asetnet_ytd),
        dp_invest_val=dp_invest_val,
        dp_invest_yoy=dp_invest_yoy,
        dp_invest_ytd=dp_invest_ytd,
        dp_invest_yoy_class=growth_class(dp_invest_yoy),
        dp_invest_ytd_class=growth_class(dp_invest_ytd),
        dp_jumlah_val=dp_jumlah_val,
        dp_jumlah_yoy=dp_jumlah_yoy,
        dp_jumlah_ytd=dp_jumlah_ytd,
        dp_jumlah_yoy_class=growth_class(dp_jumlah_yoy),
        dp_jumlah_ytd_class=growth_class(dp_jumlah_ytd),
        dp_year_labels=dp_year_labels,
        dp_year_aset=dp_year_aset,
        dp_year_asetnet=dp_year_asetnet,
        dp_year_invest=dp_year_invest,
        dp_year_jumlah=dp_year_jumlah,
        dp_mini_labels=dp_mini_labels,
        dp_mini_aset=dp_mini_aset,
        dp_mini_invest=dp_mini_invest,
        dp_mini_jumlah=dp_mini_jumlah,
        dp_ratio_labels=dp_ratio_labels,
        dp_ratio_invest=dp_ratio_invest,
        dp_ratio_asetnet=dp_ratio_asetnet,
    )
    return ctx
