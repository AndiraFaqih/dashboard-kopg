# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import logging
import os

from perbankan_module import build_dashboard_context
from dana_pensiun_module import build_dana_pensiun_context
from asuransi_module import build_asuransi_context
from komoditas_module import (
    build_komoditas_context,
    build_kredit_lokasi_context,
)
from database import init_db, test_db_connection, db
from models import PerbankanSummary, Asuransi, DanaPensiun

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


def month_name(num: int | str) -> str | None:
    """Konversi angka bulan ke nama bulan Indonesia."""
    names = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]
    try:
        i = int(num)
        if 1 <= i <= 12:
            return names[i - 1]
    except Exception:
        pass
    return None


def to_year(val):
    """Ambil maksimal 4 digit tahun, atau None."""
    if val in (None, ""):
        return None
    s = str(val).strip()
    if not s:
        return None
    return int(s[:4]) if s[:4].isdigit() else None

# Initialize database
logger.info("=" * 50)
logger.info("🚀 Memulai aplikasi Flask...")
logger.info("=" * 50)
init_db(app)
logger.info("=" * 50)

# -------------------------------------------------
# ROUTE DASHBOARD PERBANKAN (utama)
# -------------------------------------------------
@app.route("/")
def dashboard():
    ctx = build_dashboard_context(request)
    return render_template("dashboard.html", **ctx)


# -------------------------------------------------
# ROUTE ALIAS UNTUK KOMPATIBILITAS
# -------------------------------------------------
@app.route("/dashboard/perbankan")
def dashboard_perbankan():
    return redirect(url_for('dashboard'))


# -------------------------------------------------
# ROUTE DASHBOARD DANA PENSIUN
# -------------------------------------------------
@app.route("/dashboard/nonbank/dana-pensiun")
def dashboard_dana_pensiun():
    ctx = build_dana_pensiun_context(request)
    return render_template("dashboard_dana_pensiun.html", **ctx)


# -------------------------------------------------
# ROUTE DASHBOARD ASURANSI
# -------------------------------------------------
@app.route("/dashboard/nonbank/asuransi")
def dashboard_asuransi():
    ctx = build_asuransi_context(request)
    return render_template("dashboard_asuransi.html", **ctx)


# -------------------------------------------------
# ROUTE DASHBOARD komoditas
# -------------------------------------------------
# -------------------------------------------------
# ROUTE DASHBOARD komoditas + kredit lokasi
# -------------------------------------------------
@app.route("/dashboard/komoditas")
def dashboard_komoditas():
    kom_ctx = build_komoditas_context(request)
    krl_ctx = build_kredit_lokasi_context(request)
    kom_ctx.update(krl_ctx)  # gabung kedua context
    return render_template("dashboard_komoditas.html", **kom_ctx)


# -------------------------------------------------
# ROUTE INPUT DATA
# -------------------------------------------------
@app.route("/input-data")
def input_data():
    return render_template("input_data.html")


@app.route("/submit-data/perbankan", methods=["POST"])
def submit_data_perbankan():
    def to_float(val):
        try:
            return float(str(val).replace(",", ".").replace(" ", "")) if val not in (None, "") else None
        except Exception:
            return None

    try:
        bulan_input = request.form.get("bulan")
        data = {
            "negara": "INDONESIA",
            "provinsi": request.form.get("provinsi", "").strip() or None,
            "tahun": to_year(request.form.get("tahun")),
            "bulan": month_name(bulan_input) if bulan_input else None,
            "total_aset": to_float(request.form.get("total_aset")),
            "giro": to_float(request.form.get("giro")),
            "tabungan": to_float(request.form.get("tabungan")),
            "deposito": to_float(request.form.get("deposito")),
            "total_dpk": to_float(request.form.get("total_dpk")),
            "modal_kerja": to_float(request.form.get("modal_kerja")),
            "investasi": to_float(request.form.get("investasi")),
            "konsumsi": to_float(request.form.get("konsumsi")),
            "total_kredit": to_float(request.form.get("total_kredit")),
            "nominal_npl_gross": to_float(request.form.get("nominal_npl_gross")),
            "rasio_npl_gross": to_float(request.form.get("rasio_npl_gross")),
            "nominal_npl_net": to_float(request.form.get("nominal_npl_net")),
            "rasio_npl_net": to_float(request.form.get("rasio_npl_net")),
            "loan_to_deposit_ratio_ldr": to_float(request.form.get("loan_to_deposit_ratio_ldr")),
        }

        record = PerbankanSummary(**data)
        db.session.add(record)
        db.session.commit()
        flash("Data perbankan berhasil disimpan.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Gagal simpan data perbankan: {e}")
        flash(f"Gagal menyimpan data perbankan: {e}", "danger")
    return redirect(url_for("input_data"))


@app.route("/submit-data/nonbank", methods=["POST"])
def submit_data_nonbank():
    flash("Gunakan form khusus Asuransi atau Dana Pensiun di bawah.", "info")
    return redirect(url_for("input_data"))


@app.route("/submit-data/asuransi", methods=["POST"])
def submit_data_asuransi():
    def to_float(val):
        try:
            return float(str(val).replace(",", ".").replace(" ", "")) if val not in (None, "") else None
        except Exception:
            return None

    def to_int(val):
        try:
            return int(val) if val not in (None, "") else None
        except Exception:
            return None

    try:
        data = {
            "provinsi": request.form.get("provinsi", "").strip() or None,
            "kabupaten": request.form.get("kabupaten", "").strip() or None,
            "periode": request.form.get("periode", "").strip() or None,
            "tahun": to_year(request.form.get("tahun")),
            "jenis": request.form.get("jenis", "").strip() or None,
            "premi": to_float(request.form.get("premi")),
            "klaim": to_float(request.form.get("klaim")),
            "jumlah_peserta_premi": to_int(request.form.get("jumlah_peserta_premi")),
            "jumlah_peserta_klaim": to_int(request.form.get("jumlah_peserta_klaim")),
            "jumlah_polis_premi": to_int(request.form.get("jumlah_polis_premi")),
            "jumlah_polis_klaim": to_int(request.form.get("jumlah_polis_klaim")),
        }

        record = Asuransi(**data)
        db.session.add(record)
        db.session.commit()
        flash("Data asuransi berhasil disimpan.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Gagal simpan data asuransi: {e}")
        flash(f"Gagal menyimpan data asuransi: {e}", "danger")
    return redirect(url_for("input_data"))


@app.route("/submit-data/dana-pensiun", methods=["POST"])
def submit_data_dana_pensiun():
    def to_float(val):
        try:
            return float(str(val).replace(",", ".").replace(" ", "")) if val not in (None, "") else None
        except Exception:
            return None

    def to_int(val):
        try:
            return int(val) if val not in (None, "") else None
        except Exception:
            return None

    try:
        bulan_input = request.form.get("bulan")
        prov = request.form.get("provinsi", "")
        data = {
            "negara": "INDONESIA",
            "provinsi": (prov.strip().upper() if prov else None),
            "bulan": month_name(bulan_input) if bulan_input else None,
            "tahun": to_year(request.form.get("tahun")),
            "jumlah_dana_pensiun": to_int(request.form.get("jumlah_dana_pensiun")),
            "aset": to_float(request.form.get("aset")),
            "aset_neto": to_float(request.form.get("aset_neto")),
            "investasi": to_float(request.form.get("investasi")),
        }

        record = DanaPensiun(**data)
        db.session.add(record)
        db.session.commit()
        flash("Data dana pensiun berhasil disimpan.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Gagal simpan data dana pensiun: {e}")
        flash(f"Gagal menyimpan data dana pensiun: {e}", "danger")
    return redirect(url_for("input_data"))


# -------------------------------------------------
# ROUTE TEST DATABASE CONNECTION
# -------------------------------------------------
@app.route("/test-db")
def test_db():
    """Test database connection and return status"""
    result = test_db_connection()
    return jsonify(result)


if __name__ == "__main__":
    logger.info("🌐 Server Flask siap berjalan pada mode debug")
    logger.info("📡 Aplikasi dapat diakses di http://127.0.0.1:5000")
    app.run(debug=True)
