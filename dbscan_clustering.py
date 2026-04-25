import os
import pandas as pd
import seaborn as sns
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# Folder output
os.makedirs('output', exist_ok=True)

# Baca dataset
df = pd.read_csv('dataset/viirs-snpp_2024_Indonesia.csv')

# Preprocessing: Konversi Confidence ke Numerik untuk analisis statistik
# l (low)=1, n (nominal)=2, h (high)=3
mapping = {'l': 1, 'n': 2, 'h': 3}
df['conf_score'] = df['confidence'].map(mapping)

# Lihat kolom yang tersedia dari dataset
print('Kolom yang tersedia:', df.columns.tolist())

# CLUSTERING
# Menyiapkan data koordinat
X = df[['latitude', 'longitude']]

# Menjalankan DBSCAN
db = DBSCAN(eps=0.1, min_samples=5).fit(X)

# Tambahkan hasil label klaster ke dalam dataframe
df['cluster'] = db.labels_

# Ringkasan hasil
print('Jumlah klaster yang ditemukan:', len(set(db.labels_)) - (1 if -1 in db.labels_ else 0))
print('Jumlah titik yang dianggap noise (-1):', list(db.labels_).count(-1))
print(df[['latitude', 'longitude', 'cluster']].head(10))

# Simpan hasil clustering
df.to_csv('output/hasil_cluster_dbscan.csv', index=False)


# VISUALISASI KLASTER
# Memisahkan data yang masuk klaster dan noise
cluster_data = df[df['cluster'] != -1]
noise_data = df[df['cluster'] == -1]

# Membuat plot
plt.figure(figsize=(12, 8), dpi=300)

plt.scatter(noise_data['longitude'], noise_data['latitude'],
            c='lightgrey', label='Noise', s=2, alpha=0.5)

scatter = plt.scatter(cluster_data['longitude'], cluster_data['latitude'],
                      c=cluster_data['cluster'], cmap='tab20',
                      label='Cluster', s=10)

plt.title('Peta Sebaran Hotspot dengan DBSCAN (VIIRS-SNPP 2024)', fontsize=14)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

# Simpan gambar
plt.savefig('output/peta_cluster_hotspot.png', dpi=300, bbox_inches='tight')
plt.close()

# ANALISIS SUHU KECERAHAN, FRP, DAN CONFIDENCE
# Menghitung rata-rata suhu, FRP, confidence dan jumlah titik per klaster
cluster_analysis = df[df['cluster'] != -1].groupby('cluster').agg({
    'bright_ti4': 'mean',
    'frp': 'mean',
    'conf_score': 'mean',
    'latitude': 'count'
}).rename(columns={'latitude': 'titik_count'})

# Mengurutkan berdasarkan suhu rata-rata tertinggi
cluster_analysis = cluster_analysis.sort_values(by='bright_ti4', ascending=False)

# Menampilkan hasil
print('Analisis Statistik per Klaster (Suhu, FRP, Confidence):')
print(cluster_analysis.head(10))

# Analisis Korelasi
correlation = df[['bright_ti4', 'frp', 'conf_score']].corr()
print('\nMatriks Korelasi antar Variabel:')
print(correlation)

# VISUALISASI HEATMAP KORELASI
plt.figure(figsize=(6,5), dpi=300)

sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")

plt.title('Heatmap Korelasi Brightness, FRP, dan Confidence')

plt.savefig('output/heatmap_korelasi.png', dpi=300, bbox_inches='tight')
plt.close()

# Melihat titik tertinggi di klaster paling panas
top_cluster = cluster_analysis.index[0]
print(f'\nTitik dengan suhu tertinggi di klaster {top_cluster}:')
print(df[df['cluster'] == top_cluster].sort_values(by='bright_ti4', ascending=False).head(3))

# Simpan analisis klaster dan matriks korelasi
cluster_analysis.to_csv('output/analisis_per_cluster.csv')
correlation.to_csv('output/matriks_korelasi.csv')