"""
Dashboard Keuangan Perbankan - Flask Server
Melayani data untuk kwd-dashboard frontend
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime
from functools import lru_cache

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'kwd-dashboard', 'dist'),
            static_folder=os.path.join(os.path.dirname(__file__), 'kwd-dashboard', 'dist'),
            static_url_path='')

# -------------------------------------------------
# KONFIGURASI FILE EXCEL
# -------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "KINERJA PERBANKAN.xlsx")

@lru_cache(maxsize=1)
def load_data():
    """Load data utama dari sheet SUMMARY"""
    df = pd.read_excel(DATA_PATH, sheet_name="SUMMARY")
    df.columns = df.columns.astype(str).str.strip()

    expected_cols = [
        "Negara", "Provinsi", "Tahun", "Bulan", "Total Aset", "Giro", "Tabungan",
        "Deposito", "Total DPK", "Modal Kerja", "Investasi", "Konsumsi",
        "Total Kredit", "Nominal NPL Gross", "Rasio NPL Gross", "Nominal NPL Net",
        "Rasio NPL Net", "Loan to Deposit Rastio (LDR)",
    ]
    
    df["Tahun"] = df["Tahun"].astype(int)

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

    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int)

    def clean_number_series(s):
        return (s.astype(str).str.strip().str.replace(" ", "", regex=False)
                 .str.replace(".", "", regex=False).str.replace(",", ".", regex=False))

    nominal_cols = [
        "Total Aset", "Giro", "Tabungan", "Deposito", "Total DPK",
        "Modal Kerja", "Investasi", "Konsumsi", "Total Kredit",
        "Nominal NPL Gross", "Nominal NPL Net",
    ]
    for col in nominal_cols:
        if df[col].dtype == object:
            df[col] = clean_number_series(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    ratio_cols = ["Rasio NPL Gross", "Rasio NPL Net", "Loan to Deposit Rastio (LDR)"]
    for col in ratio_cols:
        if df[col].dtype == object:
            df[col] = (df[col].astype(str).str.strip().str.replace("%", "", regex=False)
                       .str.replace(" ", "", regex=False).str.replace(",", ".", regex=False))
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


@lru_cache(maxsize=1)
def load_umkm_data():
    """Load data UMKM"""
    df = pd.read_excel(DATA_PATH, sheet_name="PERBANKAN - Per Jenis Usaha")
    df.columns = (df.columns.astype(str).str.replace("\n", " ", regex=False)
                  .str.replace("\r", " ", regex=False).str.replace('"', "", regex=False)
                  .str.strip().str.replace(r"\s+", " ", regex=True))

    def find_col(keyword, exclude=None):
        cols = list(df.columns)
        candidates = [c for c in cols if keyword in c and (exclude is None or exclude not in c)]
        if not candidates:
            raise ValueError(f"Tidak menemukan kolom yang mengandung '{keyword}'. Kolom: {cols}")
        return candidates[0]

    df = df.rename(columns={
        find_col("Provinsi"): "Provinsi",
        find_col("Tahun"): "Tahun",
        find_col("Bulan"): "Bulan",
        find_col("Jenis Kredit"): "Jenis",
        find_col("Nominal Kredit"): "Nominal Kredit",
        find_col("Nominal NPL", exclude="Net"): "Nominal NPL",
        find_col("Nominal NPL Net"): "Nominal NPL Net",
        find_col("Jumlah Rekening UMKM"): "Jumlah Rekening UMKM",
    })

    df["Tahun"] = df["Tahun"].astype(int)
    df["Bulan"] = df["Bulan"].apply(parse_bulan).astype(int) if "Bulan" in df.columns else 1

    def clean_num(s):
        return (s.astype(str).str.strip().str.replace(" ", "", regex=False)
                 .str.replace(".", "", regex=False).str.replace(",", ".", regex=False))

    nominal_cols = ["Nominal Kredit", "Nominal NPL", "Nominal NPL Net"]
    for col in nominal_cols:
        if col in df.columns and df[col].dtype == object:
            df[col] = clean_num(df[col])
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["periode"] = pd.to_datetime(dict(year=df["Tahun"], month=df["Bulan"], day=1))
    return df


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


def make_agg_month(df_src):
    """Aggregate ke level Tahun-Bulan"""
    agg = df_src.groupby(["Tahun", "Bulan"], as_index=False).agg({
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
        "Rasio NPL Gross": "mean",
        "Rasio NPL Net": "mean",
        "Loan to Deposit Rastio (LDR)": "mean",
    })
    agg["periode"] = pd.to_datetime(dict(year=agg["Tahun"], month=agg["Bulan"], day=1))
    return agg


def compute_growth(agg, metric, selected_year, selected_month):
    """Hitung current value, YoY, YtD"""
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
        if current is None and not year_df.empty:
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
    if v is None:
        return "secondary"
    if abs(v) < 1e-9:
        return "secondary"
    return "success" if v >= 0 else "danger"


# -------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------

@app.route("/api/data", methods=["GET"])
def get_dashboard_data():
    """Return semua data dashboard dalam format JSON"""
    try:
        df = load_data()
        
        negara_list = sorted(df["Negara"].dropna().unique().tolist())
        provinsi_list = sorted(df["Provinsi"].dropna().unique().tolist())
        tahun_list = sorted(df["Tahun"].dropna().unique().tolist())
        bulan_list = sorted(df["Bulan"].dropna().unique().tolist())

        negara = request.args.get("negara", "")
        provinsi = request.args.get("provinsi", "")
        tahun = request.args.get("tahun", "")
        bulan = request.args.get("bulan", "")
        interval = request.args.get("interval", "bulanan")

        selected_year = int(tahun) if tahun else None
        selected_month = int(bulan) if bulan else None

        df_region = df.copy()
        if negara:
            df_region = df_region[df_region["Negara"] == negara]
        if provinsi:
            df_region = df_region[df_region["Provinsi"] == provinsi]
        if df_region.empty:
            df_region = df.copy()

        agg_month_region = make_agg_month(df_region)
        agg_month_region["Kredit Produktif"] = (
            agg_month_region["Modal Kerja"] + agg_month_region["Investasi"]
        )
        agg_month_region["Kredit Konsumtif"] = agg_month_region["Konsumsi"]

        # KPI utama
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

        npl_val = npl_raw
        ldr_val = ldr_raw

        # DPK components
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

        # Kredit Produktif vs Konsumtif
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

        # Chart data
        agg_year = (
            agg_month_region.groupby(["Tahun"], as_index=False)
            .agg({"Total Aset": "sum", "Total DPK": "sum", "Total Kredit": "sum"})
            .sort_values("Tahun")
        )

        year_labels = agg_year["Tahun"].astype(str).tolist()
        year_aset_series = agg_year["Total Aset"].tolist()
        year_dpk_series = agg_year["Total DPK"].tolist()
        year_kredit_series = agg_year["Total Kredit"].tolist()

        # Mini bars (3 periode terakhir)
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
            tmp = tmp.groupby(["Tahun", "Triwulan"], as_index=False).agg({
                "Total Aset": "sum", "Total DPK": "sum", "Total Kredit": "sum",
            })
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
            tmp = tmp.groupby(["Tahun", "Semester"], as_index=False).agg({
                "Total Aset": "sum", "Total DPK": "sum", "Total Kredit": "sum",
            })
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
                .agg({"Total Aset": "sum", "Total DPK": "sum", "Total Kredit": "sum"})
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

        # NPL & LDR tahunan
        dec_all = agg_month_region[agg_month_region["Bulan"] == 12].sort_values("Tahun")
        npl_labels = [f"Des'{str(y)[-2:]}" for y in dec_all["Tahun"]]
        npl_series = dec_all["Rasio NPL Gross"].tolist()
        ldr_series = dec_all["Loan to Deposit Rastio (LDR)"].tolist()

        # UMKM Data
        df_umkm = load_umkm_data()
        umkm_region = df_umkm.copy()
        if provinsi:
            umkm_region = umkm_region[umkm_region["Provinsi"] == provinsi]
        if umkm_region.empty:
            umkm_region = df_umkm.copy()

        agg_umkm = (
            umkm_region.groupby(["Tahun", "Bulan"], as_index=False)
            .agg({
                "Nominal Kredit": "sum",
                "Nominal NPL": "sum",
                "Nominal NPL Net": "sum",
                "Jumlah Rekening UMKM": "sum",
            })
            .sort_values(["Tahun", "Bulan"])
        )
        agg_umkm["periode"] = pd.to_datetime(
            dict(year=agg_umkm["Tahun"], month=agg_umkm["Bulan"], day=1)
        )

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
            .agg({
                "Nominal Kredit": "sum",
                "NPL Ratio": "mean",
                "Kredit per Rekening": "mean",
            })
            .sort_values("Tahun")
        )
        umkm_year_labels = agg_umkm_year["Tahun"].astype(str).tolist()
        umkm_year_kredit = agg_umkm_year["Nominal Kredit"].tolist()
        umkm_year_npl_ratio = agg_umkm_year["NPL Ratio"].tolist()
        umkm_year_kpr = agg_umkm_year["Kredit per Rekening"].tolist()

        return jsonify({
            "filters": {
                "negara_list": negara_list,
                "provinsi_list": provinsi_list,
                "tahun_list": tahun_list,
                "bulan_list": bulan_list,
                "negara_selected": negara,
                "provinsi_selected": provinsi,
                "tahun_selected": tahun,
                "bulan_selected": bulan,
                "interval_selected": interval,
            },
            "kpi": {
                "aset_val": float(aset_val),
                "aset_yoy": float(aset_yoy) if aset_yoy else 0,
                "aset_ytd": float(aset_ytd) if aset_ytd else 0,
                "aset_yoy_class": growth_class(aset_yoy),
                "aset_ytd_class": growth_class(aset_ytd),
                "dpk_val": float(dpk_val),
                "dpk_yoy": float(dpk_yoy) if dpk_yoy else 0,
                "dpk_ytd": float(dpk_ytd) if dpk_ytd else 0,
                "dpk_yoy_class": growth_class(dpk_yoy),
                "dpk_ytd_class": growth_class(dpk_ytd),
                "kredit_val": float(kredit_val),
                "kredit_yoy": float(kredit_yoy) if kredit_yoy else 0,
                "kredit_ytd": float(kredit_ytd) if kredit_ytd else 0,
                "kredit_yoy_class": growth_class(kredit_yoy),
                "kredit_ytd_class": growth_class(kredit_ytd),
                "npl_val": float(npl_val),
                "npl_yoy": float(npl_yoy) if npl_yoy else 0,
                "npl_ytd": float(npl_ytd) if npl_ytd else 0,
                "npl_yoy_class": growth_class(npl_yoy),
                "npl_ytd_class": growth_class(npl_ytd),
                "ldr_val": float(ldr_val),
                "ldr_yoy": float(ldr_yoy) if ldr_yoy else 0,
                "ldr_ytd": float(ldr_ytd) if ldr_ytd else 0,
                "ldr_yoy_class": growth_class(ldr_yoy),
                "ldr_ytd_class": growth_class(ldr_ytd),
            },
            "shares": {
                "share_giro": round(share_giro, 2),
                "share_tab": round(share_tab, 2),
                "share_dep": round(share_dep, 2),
                "share_kons": round(share_kons, 2),
                "share_prod": round(share_prod, 2),
                "share_mk": round(share_mk, 2),
                "share_inv": round(share_inv, 2),
            },
            "charts": {
                "mini_labels": mini_labels,
                "mini_aset": mini_aset,
                "mini_dpk": mini_dpk,
                "mini_kredit": mini_kredit,
                "year_labels": year_labels,
                "year_aset": year_aset_series,
                "year_dpk": year_dpk_series,
                "year_kredit": year_kredit_series,
                "npl_labels": npl_labels,
                "npl_series": npl_series,
                "ldr_series": ldr_series,
            },
            "umkm": {
                "kredit_val": float(umkm_kredit_val),
                "kredit_yoy": float(umkm_kredit_yoy) if umkm_kredit_yoy else 0,
                "kredit_ytd": float(umkm_kredit_ytd) if umkm_kredit_ytd else 0,
                "kredit_yoy_class": growth_class(umkm_kredit_yoy),
                "kredit_ytd_class": growth_class(umkm_kredit_ytd),
                "npl_val": float(umkm_npl_val),
                "npl_yoy": float(umkm_npl_yoy) if umkm_npl_yoy else 0,
                "npl_ytd": float(umkm_npl_ytd) if umkm_npl_ytd else 0,
                "npl_yoy_class": growth_class(umkm_npl_yoy),
                "npl_ytd_class": growth_class(umkm_npl_ytd),
                "npl_net_val": float(umkm_npl_net_val),
                "npl_net_yoy": float(umkm_npl_net_yoy) if umkm_npl_net_yoy else 0,
                "npl_net_ytd": float(umkm_npl_net_ytd) if umkm_npl_net_ytd else 0,
                "npl_net_yoy_class": growth_class(umkm_npl_net_yoy),
                "npl_net_ytd_class": growth_class(umkm_npl_net_ytd),
                "rek_val": float(umkm_rek_val),
                "rek_yoy": float(umkm_rek_yoy) if umkm_rek_yoy else 0,
                "rek_ytd": float(umkm_rek_ytd) if umkm_rek_ytd else 0,
                "rek_yoy_class": growth_class(umkm_rek_yoy),
                "rek_ytd_class": growth_class(umkm_rek_ytd),
                "npl_ratio_val": float(umkm_npl_ratio_val),
                "npl_ratio_yoy": float(umkm_npl_ratio_yoy) if umkm_npl_ratio_yoy else 0,
                "npl_ratio_ytd": float(umkm_npl_ratio_ytd) if umkm_npl_ratio_ytd else 0,
                "npl_ratio_yoy_class": growth_class(umkm_npl_ratio_yoy),
                "npl_ratio_ytd_class": growth_class(umkm_npl_ratio_ytd),
                "kpr_val": float(umkm_kpr_val),
                "kpr_yoy": float(umkm_kpr_yoy) if umkm_kpr_yoy else 0,
                "kpr_ytd": float(umkm_kpr_ytd) if umkm_kpr_ytd else 0,
                "kpr_yoy_class": growth_class(umkm_kpr_yoy),
                "kpr_ytd_class": growth_class(umkm_kpr_ytd),
                "year_labels": umkm_year_labels,
                "year_kredit": umkm_year_kredit,
                "year_npl_ratio": umkm_year_npl_ratio,
                "year_kpr": umkm_year_kpr,
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    """Serve landing page"""
    landing_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(landing_path):
        with open(landing_path, 'r', encoding='utf-8') as f:
            return f.read()
    return redirect('/keuangan')


@app.route("/keuangan")
def keuangan():
    """Halaman dashboard keuangan"""
    # Serve the built HTML from kwd-dashboard dist folder
    keuangan_path = os.path.join(os.path.dirname(__file__), 'kwd-dashboard', 'dist', 'keuangan.html')
    if os.path.exists(keuangan_path):
        with open(keuangan_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fallback to standalone if dist doesn't exist
    keuangan_fallback = os.path.join(os.path.dirname(__file__), 'kwd-dashboard', 'src', 'html', 'keuangan-standalone.html')
    if os.path.exists(keuangan_fallback):
        with open(keuangan_fallback, 'r', encoding='utf-8') as f:
            return f.read()
    
    return "File keuangan.html tidak ditemukan", 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)

@app.route("/test-dashboard")
def test_dashboard():
    """Simple test dashboard"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Test Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .kpi { display: inline-block; width: 23%; margin: 1%; padding: 20px; background: #f0f0f0; border-radius: 8px; text-align: center; }
        canvas { width: 100% !important; height: auto; }
    </style>
</head>
<body>
    <h1>�� Test Dashboard Data Loading</h1>
    
    <div class="card">
        <h2>Status</h2>
        <div id="status" style="padding: 10px; background: #fff3cd; border-radius: 4px;">⏳ Initializing...</div>
    </div>

    <div class="card">
        <h2>📊 KPI Cards</h2>
        <div class="kpi"><strong>Aset</strong><br><div id="aset" style="font-size: 24px; font-weight: bold; margin-top: 10px;">-</div></div>
        <div class="kpi"><strong>Kredit</strong><br><div id="kredit" style="font-size: 24px; font-weight: bold; margin-top: 10px;">-</div></div>
        <div class="kpi"><strong>DPK</strong><br><div id="dpk" style="font-size: 24px; font-weight: bold; margin-top: 10px;">-</div></div>
        <div class="kpi"><strong>NPL</strong><br><div id="npl" style="font-size: 24px; font-weight: bold; margin-top: 10px;">-</div></div>
    </div>

    <div class="card">
        <h2>📈 Mini Chart - Aset</h2>
        <canvas id="miniChart" height="60"></canvas>
    </div>

    <div class="card">
        <h2>🥧 Pie Chart - DPK</h2>
        <canvas id="pieChart" height="80"></canvas>
    </div>

    <script>
        async function loadDashboard() {
            try {
                document.getElementById('status').innerHTML = '⏳ Loading API data...';
                
                const response = await fetch('/api/data');
                if (!response.ok) throw new Error('HTTP ' + response.status);
                
                const data = await response.json();
                console.log('✅ Data loaded:', data);
                document.getElementById('status').innerHTML = '✅ Data loaded successfully!';
                
                // Format helper
                const fmt = (n) => new Intl.NumberFormat('id-ID', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(n);
                
                // Update KPI
                document.getElementById('aset').textContent = 'Rp ' + fmt(data.kpi.aset_val / 1e12) + 'T';
                document.getElementById('kredit').textContent = 'Rp ' + fmt(data.kpi.kredit_val / 1e12) + 'T';
                document.getElementById('dpk').textContent = 'Rp ' + fmt(data.kpi.dpk_val / 1e12) + 'T';
                document.getElementById('npl').textContent = fmt(data.kpi.npl_val) + '%';
                
                // Mini chart
                new Chart(document.getElementById('miniChart'), {
                    type: 'bar',
                    data: {
                        labels: data.charts.mini_labels,
                        datasets: [{label: 'Aset', data: data.charts.mini_aset, backgroundColor: '#3b82f6'}]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: {legend: {display: false}} }
                });
                
                // Pie chart
                const s = data.shares;
                new Chart(document.getElementById('pieChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Giro', 'Tabungan', 'Deposito'],
                        datasets: [{data: [s.share_giro, s.share_tab, s.share_dep], backgroundColor: ['#3b82f6', '#10b981', '#f59e0b']}]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: {legend: {position: 'bottom'}} }
                });
                
            } catch(e) {
                document.getElementById('status').innerHTML = '❌ Error: ' + e.message;
                console.error(e);
            }
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadDashboard);
        } else {
            loadDashboard();
        }
    </script>
</body>
</html>'''
