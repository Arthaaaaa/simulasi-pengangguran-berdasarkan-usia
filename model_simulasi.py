import pandas as pd
import matplotlib.pyplot as plt

# 1. BACA DATA
# -------------
# Pastikan file data_pengangguran.csv ada di folder yang sama
df = pd.read_csv("data_pengangguran.csv")

# Cek 5 baris pertama (optional, hanya untuk debugging)
print("5 baris pertama:")
print(df.head())

# 2. BERSIHKAN DAN PILIH DATA YANG DIPAKAI
# ----------------------------------------
# Kita hanya ambil baris dengan Golongan_Umur = 'Total'
df_total = df[df["Golongan_Umur"] == "Total"].copy()

# Kita buat kolom 'Periode' gabungan Tahun + Bulan, misalnya '2021-Feb'
df_total["Periode"] = df_total["Tahun"].astype(str) + "-" + df_total["Bulan"]

# Sekarang kita pivot:
# index = Periode
# kolom = Status (Pernah, Tidak, Jumlah_penggaguran)
# nilai = Jumlah
pivot = df_total.pivot(index="Periode", columns="Status", values="Jumlah")

# Urutkan berdasarkan waktu (kalau urutannya belum benar)
pivot = pivot.sort_index()

print("\nData total per periode:")
print(pivot)

# Pastikan kolom yang tersedia
print("\nKolom di pivot:", pivot.columns)

# 3. SIMULASI DINAMIK SEDERHANA
# -----------------------------
# Kita akan anggap:
#   - 'Pernah'   = jumlah pengangguran yang pernah bekerja sebelumnya
#   - 'Tidak'    = pengangguran yang belum pernah bekerja
#   - Kita bikin model mainan:
#       Setiap langkah waktu (dari satu periode ke periode berikutnya):
#         - Sebagian penganggur 'Tidak' dapat kerja
#         - Sebagian penganggur 'Pernah' dapat kerja
#         - Ada pendatang baru jadi penganggur 'Tidak' (lulusan/pencari kerja baru)
#
# Ini bukan model sempurna, tapi cukup untuk contoh System Dynamics diskrit.

# Ambil data awal dari periode pertama (misal 2021-Feb)
awal_periode = pivot.index[0]
U_pernah_awal = pivot.loc[awal_periode, "Pernah"]
U_tidak_awal = pivot.loc[awal_periode, "Tidak"]

print(f"\nPeriode awal: {awal_periode}")
print("U_pernah_awal =", U_pernah_awal)
print("U_tidak_awal  =", U_tidak_awal)

# Parameter model (boleh kamu eksperimen nanti)
rate_dapat_kerja_pernah = 0.10   # 10% penganggur berpengalaman dapat kerja tiap langkah
rate_dapat_kerja_tidak  = 0.05   # 5% penganggur tanpa pengalaman dapat kerja tiap langkah
rate_pendatang_baru     = 0.03   # 3% dari total penganggur menjadi "pendatang baru" ke kelompok 'Tidak'

# Kita simulasikan sebanyak jumlah periode data (supaya sebanding)
jumlah_langkah = len(pivot.index)

# List untuk menyimpan hasil simulasi tiap langkah
sim_periode = []
sim_pernah = []
sim_tidak = []

# Nilai awal
U_pernah = U_pernah_awal
U_tidak = U_tidak_awal

for step in range(jumlah_langkah):
    periode = pivot.index[step]  # pakai nama periode dari data asli untuk label
    
    sim_periode.append(periode)
    sim_pernah.append(U_pernah)
    sim_tidak.append(U_tidak)
    
    # Hitung total penganggur saat ini
    total_U = U_pernah + U_tidak
    
    # Hitung berapa orang yang:
    # - dapat kerja dari kelompok pernah dan tidak
    # - masuk baru sebagai penganggur tanpa pengalaman
    dapat_kerja_pernah = rate_dapat_kerja_pernah * U_pernah
    dapat_kerja_tidak = rate_dapat_kerja_tidak * U_tidak
    pendatang_baru = rate_pendatang_baru * total_U
    
    # Update stok (System Dynamics diskrit):
    # Penganggur berpengalaman berkurang karena dapat kerja
    U_pernah = U_pernah - dapat_kerja_pernah
    
    # Penganggur tanpa pengalaman:
    #   + pendatang baru
    #   - yang dapat kerja
    U_tidak = U_tidak + pendatang_baru - dapat_kerja_tidak

# 4. BANDINGKAN DATA ASLI VS SIMULASI (GRAFIK)
# --------------------------------------------
plt.figure()
plt.plot(pivot.index, pivot["Pernah"], marker="o", label="Data Asli - Pernah")
plt.plot(pivot.index, pivot["Tidak"], marker="o", label="Data Asli - Tidak")

plt.plot(sim_periode, sim_pernah, linestyle="--", label="Simulasi - Pernah")
plt.plot(sim_periode, sim_tidak, linestyle="--", label="Simulasi - Tidak")

plt.xticks(rotation=45)
plt.xlabel("Periode")
plt.ylabel("Jumlah Penganggur")
plt.title("Perbandingan Data Asli vs Simulasi\n(Pernah vs Tidak Pernah Bekerja)")
plt.legend()
plt.tight_layout()
plt.show()
