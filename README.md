# Analisis Spasial Hotspot VIIRS-SNPP Indonesia 2024

Proyek ini bertujuan untuk mengidentifikasi pola sebaran titik panas (*hotspot*) di Indonesia sepanjang tahun 2024 menggunakan algoritma *Density-Based Spatial Clustering of Applications with Noise* (**DBSCAN**). Analisis berfokus pada pemetaan kepadatan geografis, intensitas energi (*Fire Radiative Power* / FRP), karakteristik termal, serta pola temporal bulanan untuk melihat sebaran dan karakteristik hotspot secara spasial.

## 1. Data yang Digunakan
Data yang diolah adalah dataset satelit **VIIRS-SNPP** untuk wilayah Indonesia tahun 2024 (`dataset/viirs-snpp_2024_Indonesia.csv`). Dataset ini berisi informasi deteksi termal satelit yang mencakup koordinat geografis, tanggal akuisisi, dan parameter intensitas api.

## 2. Variabel/Kolom yang Digunakan
Dalam analisis ini, kolom yang dipilih disesuaikan dengan kebutuhan pemodelan statistik dan spasial:

* **Koordinat (Spasial):** `latitude`, `longitude` sebagai input utama DBSCAN.
* **Temporal:** `acq_date` yang diubah menjadi kolom `month` untuk rekap bulanan.
* **Intensitas & Validitas:**
    * `bright_ti4`: Suhu kecerahan (*brightness temperature*).
    * `frp`: *Fire Radiative Power* (intensitas energi kebakaran).
    * `confidence`: Tingkat keyakinan deteksi yang dikonversi menjadi `conf_score` untuk analisis statistik: *low=1, nominal=2, high=3*.

## 3. Metodologi Analisis
1.  **Preprocessing:** Konversi data kategori `confidence` menjadi numerik untuk kebutuhan komputasi statistik.
2.  **Analisis Temporal:** Rekap jumlah hotspot per bulan berdasarkan `acq_date`.
3.  **K-Distance Plot:** Perhitungan jarak tetangga ke-5 untuk membantu menilai nilai `eps` yang sesuai pada DBSCAN.
4.  **Clustering:** Penerapan DBSCAN dengan parameter `eps=0.1` dan `min_samples=100` untuk mengelompokkan titik api yang berdekatan secara geografis.
5.  **Evaluasi Klaster:** Pengukuran kualitas hasil DBSCAN menggunakan *Davies-Bouldin Index*, *Silhouette Score*, dan *Calinski-Harabasz Index* jika jumlah klaster valid mencukupi.
6.  **Analisis Statistik:** Agregasi rata-rata `bright_ti4`, `frp`, dan `conf_score` per klaster untuk mengukur karakteristik tiap area kebakaran.
7.  **Korelasi:** Evaluasi hubungan statistik antara suhu kecerahan, energi, dan tingkat keyakinan data menggunakan korelasi Pearson.

## 4. Output Analisis
Program ini menghasilkan file di dalam folder `output/`:

* **CSV Files:**
    * `hasil_cluster_dbscan.csv`: Dataset asli dengan tambahan label klaster untuk setiap titik.
    * `analisis_temporal_bulanan.csv`: Rekap jumlah hotspot per bulan.
    * `analisis_per_cluster.csv`: Ringkasan statistik per klaster berisi rata-rata `bright_ti4`, `frp`, `conf_score`, dan jumlah titik.
    * `hasil_evaluasi_klaster.csv`: Hasil evaluasi klaster menggunakan DBI, Silhouette Score, dan Calinski-Harabasz Index.
    * `matriks_korelasi.csv`: Matriks hubungan antar variabel.
* **Visualisasi (PNG):**
    * `tren_hotspot_bulanan.png`: Grafik jumlah hotspot per bulan.
    * `peta_cluster_hotspot.png`: Visualisasi sebaran klaster hotspot di peta Indonesia.
    * `heatmap_korelasi.png`: Matriks korelasi antar variabel untuk melihat kekuatan hubungan data.
    * `k_distance_plot.png`: Plot k-distance untuk membantu pemilihan parameter `eps` pada DBSCAN.

---
*Dibuat untuk keperluan analisis data spasial kebakaran hutan dan lahan.*
