# Analisis Spasial Hotspot VIIRS-SNPP Indonesia 2024

Proyek ini bertujuan untuk mengidentifikasi pola sebaran titik panas (*hotspot*) di Indonesia sepanjang tahun 2024 menggunakan algoritma *Density-Based Spatial Clustering of Applications with Noise* (**DBSCAN**). Analisis ini berfokus pada pemetaan kepadatan geografis, intensitas energi (FRP), dan karakteristik termal untuk mengidentifikasi area rawan kebakaran hutan dan lahan secara spasial.

## 1. Data yang Digunakan
Data yang diolah adalah dataset satelit **VIIRS-SNPP** untuk wilayah Indonesia tahun 2024 (`viirs-snpp_2024_Indonesia.csv`). Dataset ini berisi informasi deteksi termal satelit yang mencakup koordinat geografis dan parameter intensitas api.

## 2. Variabel/Kolom yang Digunakan
Dalam analisis ini, kolom yang dipilih disesuaikan dengan kebutuhan pemodelan statistik dan spasial:

* **Koordinat (Spasial):** `latitude`, `longitude` (Input utama untuk DBSCAN).
* **Intensitas & Validitas:**
    * `bright_ti4`: Suhu kecerahan (*brightness temperature*).
    * `frp`: *Fire Radiative Power* (intensitas energi kebakaran).
    * `confidence`: Tingkat keyakinan deteksi (dikonversi menjadi `conf_score` untuk analisis statistik: *low=1, nominal=2, high=3*).

## 3. Metodologi Analisis
1.  **Preprocessing:** Konversi data kategori `confidence` menjadi numerik untuk kebutuhan komputasi statistik.
2.  **Clustering:** Penerapan DBSCAN dengan parameter `eps=0.1` dan `min_samples=5` untuk mengelompokkan titik api yang berdekatan secara geografis.
3.  **Analisis Statistik:** Agregasi rata-rata `bright_ti4`, `frp`, dan `conf_score` per klaster untuk mengukur tingkat signifikansi dan kepadatan tiap area kebakaran.
4.  **Korelasi:** Evaluasi hubungan statistik antara suhu kecerahan, energi, dan tingkat keyakinan data menggunakan *Pearson Correlation*.

## 4. Output Analisis
Program ini menghasilkan file di dalam folder `output/`:

* **CSV Files:**
    * `hasil_cluster_dbscan.csv`: Dataset asli dengan tambahan label klaster untuk setiap titik.
    * `analisis_per_cluster.csv`: Ringkasan statistik (rata-rata suhu, FRP, jumlah titik) per klaster.
    * `matriks_korelasi.csv`: Matriks hubungan antar variabel.
* **Visualisasi (PNG):**
    * `peta_cluster_hotspot.png`: Visualisasi sebaran klaster hotspot di peta Indonesia.
    * `heatmap_korelasi.png`: Matriks korelasi antar variabel untuk melihat kekuatan hubungan data.

---
*Dibuat untuk keperluan analisis data spasial kebakaran hutan dan lahan.*