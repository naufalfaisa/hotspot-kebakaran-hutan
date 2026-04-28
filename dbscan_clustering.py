import os
import pandas as pd
import seaborn as sns
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
import numpy as np

# Folder output
os.makedirs('output', exist_ok=True)

# Baca dataset
df = pd.read_csv('dataset/viirs-snpp_2024_Indonesia.csv')
df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')
df['month'] = df['acq_date'].dt.to_period('M').astype(str)

# Preprocessing: Konversi Confidence ke Numerik untuk analisis statistik
# l (low)=1, n (nominal)=2, h (high)=3
mapping = {'l': 1, 'n': 2, 'h': 3}
df['conf_score'] = df['confidence'].map(mapping)

# Lihat kolom yang tersedia dari dataset
print('Kolom yang tersedia:', df.columns.tolist())


# ANALISIS TEMPORAL BULANAN
monthly_hotspot = df.groupby('month').size().reset_index(name='titik_count')
monthly_hotspot = monthly_hotspot.sort_values('month')

plt.figure(figsize=(10, 5), dpi=300)
plt.plot(monthly_hotspot['month'], monthly_hotspot['titik_count'], marker='o')
plt.title('Tren Jumlah Hotspot per Bulan (VIIRS-SNPP 2024)')
plt.xlabel('Bulan')
plt.ylabel('Jumlah Titik')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('output/tren_hotspot_bulanan.png', dpi=300, bbox_inches='tight')
plt.close()

monthly_hotspot.to_csv('output/analisis_temporal_bulanan.csv', index=False)


# CLUSTERING
# Menyiapkan data koordinat
X = df[['latitude', 'longitude']]

k = 5 
neighbors = NearestNeighbors(n_neighbors=k)
neighbors_fit = neighbors.fit(X)
distances, indices = neighbors_fit.kneighbors(X)

k_distances = np.sort(distances[:, k-1], axis=0)

plt.figure(figsize=(10, 5), dpi=300)
plt.plot(k_distances)
plt.title('K-Distance Plot untuk Penentuan Epsilon (eps)')
plt.xlabel('Titik Data (diurutkan berdasarkan jarak)')
plt.ylabel(f'{k}-th Nearest Neighbor Distance')
plt.grid(True, linestyle='--')
plt.savefig('output/k_distance_plot.png')
plt.close()

# Menjalankan DBSCAN
db = DBSCAN(eps=0.1, min_samples=100).fit(X)

# Tambahkan hasil label klaster ke dalam dataframe
df['cluster'] = db.labels_

# Ringkasan hasil
print('Jumlah klaster yang ditemukan:', len(set(db.labels_)) - (1 if -1 in db.labels_ else 0))
print('Jumlah titik yang dianggap noise (-1):', list(db.labels_).count(-1))
print(df[['latitude', 'longitude', 'cluster']].head(10))

cluster_mask = df['cluster'] != -1
cluster_unique = df.loc[cluster_mask, 'cluster'].nunique()

if cluster_unique > 1:
    cluster_features = df.loc[cluster_mask, ['latitude', 'longitude']]
    cluster_labels = df.loc[cluster_mask, 'cluster']
    davies_bouldin = davies_bouldin_score(cluster_features, cluster_labels)
    silhouette = silhouette_score(
        cluster_features,
        cluster_labels,
        sample_size=min(10000, len(cluster_features))
    )
    calinski_harabasz = calinski_harabasz_score(cluster_features, cluster_labels)

    evaluation_results = pd.DataFrame([
        {'metode': 'Davies-Bouldin Index', 'nilai': davies_bouldin},
        {'metode': 'Silhouette Score', 'nilai': silhouette},
        {'metode': 'Calinski-Harabasz Index', 'nilai': calinski_harabasz},
    ])

    print('\nEvaluasi Kualitas Klaster:')
    print(f'Davies-Bouldin Index (DBI): {davies_bouldin:.4f}')
    print(f'Silhouette Score: {silhouette:.4f}')
    print(f'Calinski-Harabasz Index: {calinski_harabasz:.4f}')
    evaluation_results.to_csv('output/hasil_evaluasi_klaster.csv', index=False)
else:
    print('\nEvaluasi Kualitas Klaster dilewati karena jumlah klaster valid kurang dari 2.')

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