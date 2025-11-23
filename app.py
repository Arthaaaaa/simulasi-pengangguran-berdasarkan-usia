import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from flask import Flask, render_template, request

app = Flask(__name__)

def jalankan_simulasi(rate_pernah, rate_tidak, rate_baru):
    # Baca data
    df = pd.read_csv("data_pengangguran.csv")
    df_total = df[df["Golongan_Umur"] == "Total"].copy()
    df_total["Periode"] = df_total["Tahun"].astype(str) + "-" + df_total["Bulan"]
    pivot = df_total.pivot(index="Periode", columns="Status", values="Jumlah")
    pivot = pivot.sort_index()

    # Ambil nilai awal
    awal_periode = pivot.index[0]
    U_pernah_awal = pivot.loc[awal_periode, "Pernah"]
    U_tidak_awal = pivot.loc[awal_periode, "Tidak"]

    jumlah_langkah = len(pivot.index)

    sim_periode = []
    sim_pernah = []
    sim_tidak = []

    U_pernah = U_pernah_awal
    U_tidak = U_tidak_awal

    # Simulasi
    for step in range(jumlah_langkah):
        periode = pivot.index[step]

        sim_periode.append(periode)
        sim_pernah.append(round(U_pernah, 2))
        sim_tidak.append(round(U_tidak, 2))

        total_U = U_pernah + U_tidak
        dapat_kerja_pernah = rate_pernah * U_pernah
        dapat_kerja_tidak = rate_tidak * U_tidak
        pendatang_baru = rate_baru * total_U

        U_pernah = U_pernah - dapat_kerja_pernah
        U_tidak = U_tidak + pendatang_baru - dapat_kerja_tidak

    # Buat tabel gabungan data asli + simulasi
    tabel_data = []
    for i in range(jumlah_langkah):
        periode = sim_periode[i]
        asli_pernah = round(pivot.loc[periode, "Pernah"], 2)
        asli_tidak = round(pivot.loc[periode, "Tidak"], 2)

        tabel_data.append({
            "periode": periode,
            "asli_pernah": asli_pernah,
            "asli_tidak": asli_tidak,
            "sim_pernah": sim_pernah[i],
            "sim_tidak": sim_tidak[i]
        })

    # Grafik Data Asli
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(pivot.index, pivot["Pernah"], marker="o", label="Pernah Bekerja", color="#1976d2", linewidth=2)
    ax1.plot(pivot.index, pivot["Tidak"], marker="s", label="Tidak Pernah Bekerja", color="#d32f2f", linewidth=2)
    plt.xticks(rotation=45)
    ax1.set_xlabel("Periode")
    ax1.set_ylabel("Jumlah Penganggur")
    ax1.set_title("Data Asli Pengangguran")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()

    buf1 = BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    img_base64_asli = base64.b64encode(buf1.read()).decode("utf-8")
    plt.close(fig1)

    # Grafik Simulasi
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(sim_periode, sim_pernah, linestyle="--", marker="o", label="Simulasi - Pernah", color="#1976d2", linewidth=2)
    ax2.plot(sim_periode, sim_tidak, linestyle="--", marker="s", label="Simulasi - Tidak", color="#d32f2f", linewidth=2)
    plt.xticks(rotation=45)
    ax2.set_xlabel("Periode")
    ax2.set_ylabel("Jumlah Penganggur")
    ax2.set_title("Data Simulasi Pengangguran")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()

    buf2 = BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    img_base64_sim = base64.b64encode(buf2.read()).decode("utf-8")
    plt.close(fig2)

    return img_base64_asli, img_base64_sim, tabel_data



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rate_pernah = float(request.form["rate_pernah"])
        rate_tidak = float(request.form["rate_tidak"])
        rate_baru = float(request.form["rate_baru"])

        plot_asli, plot_sim, table = jalankan_simulasi(rate_pernah, rate_tidak, rate_baru)

        return render_template(
            "index.html",
            plot_url_asli=plot_asli,
            plot_url_sim=plot_sim,
            tabel=table,
            rate_pernah=rate_pernah,
            rate_tidak=rate_tidak,
            rate_baru=rate_baru
        )

    return render_template(
        "index.html",
        plot_url_asli=None,
        plot_url_sim=None,
        tabel=None,
        rate_pernah=0.10,
        rate_tidak=0.05,
        rate_baru=0.03
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
