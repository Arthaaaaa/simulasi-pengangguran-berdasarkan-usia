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

    # Grafik
    fig, ax = plt.subplots()
    ax.plot(pivot.index, pivot["Pernah"], marker="o", label="Data Asli - Pernah")
    ax.plot(pivot.index, pivot["Tidak"], marker="o", label="Data Asli - Tidak")
    ax.plot(sim_periode, sim_pernah, linestyle="--", label="Simulasi - Pernah")
    ax.plot(sim_periode, sim_tidak, linestyle="--", label="Simulasi - Tidak")

    plt.xticks(rotation=45)
    ax.set_xlabel("Periode")
    ax.set_ylabel("Jumlah Penganggur")
    ax.set_title("Simulasi Pengangguran Berdasarkan Pengalaman Kerja")
    ax.legend()
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    return img_base64, tabel_data



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rate_pernah = float(request.form["rate_pernah"])
        rate_tidak = float(request.form["rate_tidak"])
        rate_baru = float(request.form["rate_baru"])

        plot, table = jalankan_simulasi(rate_pernah, rate_tidak, rate_baru)

        return render_template(
            "index.html",
            plot_url=plot,
            tabel=table,
            rate_pernah=rate_pernah,
            rate_tidak=rate_tidak,
            rate_baru=rate_baru
        )

    return render_template(
        "index.html",
        plot_url=None,
        tabel=None,
        rate_pernah=0.10,
        rate_tidak=0.05,
        rate_baru=0.03
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
