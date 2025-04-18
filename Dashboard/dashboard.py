import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi visualisasi
sns.set(style="whitegrid")

# Load Data
@st.cache_data

def load_data():
    df = pd.read_csv('data_all_stations.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

data = load_data()

# Sidebar - Filter
st.sidebar.header("Filter")

# Filter Tahun
data['year'] = data['date'].dt.year
unique_years = sorted(data['year'].unique())
selected_years = st.sidebar.multiselect("Pilih Tahun", unique_years, default=unique_years)
data = data[data['year'].isin(selected_years)]

# Filter Polutan dan Stasiun
pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2']
weather_vars = ['TEMP', 'DEWP', 'PRES', 'WSPM']

selected_pols = st.sidebar.multiselect("Pilih Polutan", pollutants, default=[pollutants[0]])
stations = data['station'].unique()
selected_stations = st.sidebar.multiselect("Pilih Stasiun", stations, default=stations)

data = data[data['station'].isin(selected_stations)]

# Visualisasi
st.title("Dashboard Kualitas Udara di Berbagai Stasiun Beijing")

# Rata-rata Polutan per Stasiun
st.subheader("\nRata-Rata Polutan di Setiap Stasiun\n")
if selected_pols:
    station_avg = data.groupby('station')[selected_pols].mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    station_avg.plot(kind='bar', ax=ax)
    ax.set_title("Rata-rata Polutan per Stasiun")
    st.pyplot(fig)

# Perbandingan Weekday vs Weekend
st.subheader("\nPerbandingan Polutan di Setiap Stasiun\n")
if selected_pols:
    if 'day_type' in data.columns:
        weekday_avg = data.groupby(['station', 'day_type'])[selected_pols].mean().reset_index()
        for pol in selected_pols:
            fig2, ax2 = plt.subplots(figsize=(14, 6))
            sns.barplot(data=weekday_avg, x='station', y=pol, hue='day_type', ax=ax2)
            ax2.set_title(f'Rata-rata {pol} per Stasiun (Weekday vs Weekend)')
            ax2.set_ylabel(f'{pol} (µg/m³)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig2)

# Korelasi Heatmap
st.subheader("\nKorelasi Polutan dan Faktor Cuaca\n")
corr = data[pollutants + weather_vars].corr()
fig3, ax3 = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=ax3)
ax3.set_title('Korelasi antara Polutan dan Faktor Cuaca')
plt.tight_layout()
st.pyplot(fig3)

# Tren Bulanan PM2.5 di Stasiun Terburuk
st.subheader("\nTren Bulanan PM2.5 di Stasiun Terburuk\n")
station_avg_pm25 = data.groupby('station')['PM2.5'].mean().sort_values(ascending=False)
if not station_avg_pm25.empty:
    worst_station = station_avg_pm25.index[0]
    worst_data = data[data['station'] == worst_station].copy()
    worst_data['month'] = worst_data['date'].dt.month
    monthly_trend = worst_data.groupby(['year', 'month'])['PM2.5'].mean().reset_index()

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_trend, x='month', y='PM2.5', hue='year', marker='o', ax=ax4)
    ax4.set_title(f'Tren Bulanan PM2.5 di Stasiun {worst_station}')
    ax4.set_xlabel('Bulan')
    ax4.set_ylabel('Rata-rata PM2.5')
    ax4.grid(True)
    plt.xticks(range(1, 13))
    plt.tight_layout()
    st.pyplot(fig4)

# Scatterplot Regresi: Polutan vs Cuaca
st.subheader("\nHubungan antara Faktor Cuaca dan Polutan\n")
for pol in selected_pols:
    fig5, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig5.suptitle(f'Hubungan antara Faktor Cuaca dan {pol}', fontsize=14)
    for i, weather in enumerate(['TEMP', 'DEWP', 'WSPM']):
        sns.regplot(
            data=data,
            x=weather, y=pol,
            ax=axes[i],
            scatter_kws={'alpha': 0.3},
            line_kws={'color': 'red'}
        )
        axes[i].set_title(f'{weather} vs {pol}')
        axes[i].set_xlabel(weather)
        axes[i].set_ylabel(pol)
        axes[i].grid(True)
    st.pyplot(fig5)

# Clustering PM2.5
st.subheader("\nClustering Kualitas Udara Berdasarkan PM2.5 per Stasiun\n")
if 'PM2.5' in data.columns:
    cluster_data = data.groupby('station')['PM2.5'].mean().sort_values(ascending=False)
    def categorize_pm25(value):
        if value > 85:
            return 'Tinggi'
        elif value > 50:
            return 'Sedang'
        else:
            return 'Rendah'
    
    cluster_labels = cluster_data.apply(categorize_pm25)
    clustered_df = pd.DataFrame({
        'Rata-rata PM2.5': cluster_data,
        'Kategori Kualitas Udara': cluster_labels
    }).reset_index()

    fig6, ax6 = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=clustered_df,
        x='Rata-rata PM2.5',
        y='station',
        hue='Kategori Kualitas Udara',
        palette={'Tinggi': 'firebrick', 'Sedang': 'goldenrod', 'Rendah': 'seagreen'},
        ax=ax6
    )
    ax6.set_title('Clustering Kualitas Udara Berdasarkan PM2.5 per Stasiun')
    ax6.set_xlabel('Rata-rata PM2.5 (µg/m³)')
    ax6.set_ylabel('Stasiun')
    plt.tight_layout()
    st.pyplot(fig6)
