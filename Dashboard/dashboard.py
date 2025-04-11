import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    return pd.read_csv('data_all_stations.csv')  

data_all_stations = load_data()
pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2']  

st.title("Dashboard Kualitas Udara di Berbagai Stasiun Beijing")
st.sidebar.header("Menu")

page = st.sidebar.radio("Pilih Halaman", [
    "Clustering Kualitas Udara",
    "Rata-rata Polutan per Stasiun",
    "Perbandingan Polutan Saat Weekday vs Weekend",
])

if page == "Clustering Kualitas Udara":
    st.subheader("\nClustering Kualitas Udara\n")
    station_avg = data_all_stations.groupby('station')['PM2.5'].mean().sort_values(ascending=False)

    def categorize_pm25(value):
        if value > 85:
            return 'Tinggi'
        elif value > 50:
            return 'Sedang'
        else:
            return 'Rendah'

    cluster_labels = station_avg.apply(categorize_pm25)

    clustered_df = pd.DataFrame({
        'Rata-rata PM2.5': station_avg,
        'Kategori Kualitas Udara': cluster_labels
    }).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=clustered_df,
        x='Rata-rata PM2.5',
        y='station',
        hue='Kategori Kualitas Udara',
        palette={'Tinggi': 'firebrick', 'Sedang': 'goldenrod', 'Rendah': 'seagreen'},
        ax=ax
    )
    ax.set_title('Clustering Kualitas Udara Berdasarkan PM2.5 per Stasiun')
    ax.set_xlabel('Rata-rata PM2.5 (µg/m³)')
    ax.set_ylabel('Stasiun')
    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("""Hasil clustering menunjukkan bahwa Stasiun Dongsi dan Wanshouxigong masuk ke dalam kategori "Tinggi", yang berarti memiliki tingkat polusi udara paling buruk dibandingkan stasiun lainnya. Hal ini terlihat dari tingginya rata-rata konsentrasi PM2.5 di kedua stasiun tersebut. Sementara itu, sepuluh stasiun lainnya dikategorikan dalam kelompok "Sedang", meskipun beberapa di antaranya memiliki nilai yang mendekati ambang batas kategori tinggi.""")

elif page == "Rata-rata Polutan per Stasiun":
    selected_pol = st.selectbox("Pilih Polutan", pollutants)
    
    station_avg = data_all_stations.groupby('station')[pollutants].mean()
    pol_data = station_avg[selected_pol].sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    pol_data.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title(f'Rata-rata {selected_pol} per Stasiun')
    ax.set_ylabel(f'{selected_pol} (µg/m³)')
    ax.set_ylim(0, pol_data.max() * 1.2)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=45, ha='right')

    for i, value in enumerate(pol_data):
        ax.text(i, value + (pol_data.max() * 0.03), f'{value:.1f}',
                ha='center', fontsize=9)

    st.pyplot(fig)

    st.markdown("""
    **PM2.5** 
    - Gucheng memiliki rata-rata PM10 tertinggi (~118.9 µg/m³).
    - Dingling memiliki rata-rata PM10 terendah (~66.3 µg/m³).
                
    **PM10** 
    - PM2.5 relatif tinggi di Dongsi dan Wanshouxigong.
    - Paling rendah di Dingling dan Huairou.
                
    **NO2** 
    - Wanliu memiliki NO2 tertinggi (~57.7 µg/m³).
    - Dingling paling rendah (~27.6 µg/m³).
                
    **SO2** 
    - Konsentrasi SO2 cukup rendah secara keseluruhan.
    - Tertinggi di Changping (15.0 µg/m³), terendah di Dingling (1.7 µg/m³).
                
    **CO** 
    - CO sangat mendominasi total konsentrasi karena satuan µg/m³ yang besar.
    - Tertinggi di Wanshouxigong, terendah di Dingling.
                
    **O3** 
    - Dingling memiliki konsentrasi O3 tertinggi (~68.5 µg/m³).
    - Paling rendah di Shunyi (~43.9 µg/m³).""")


# 2. Weekday vs Weekend
elif page == "Perbandingan Polutan Saat Weekday vs Weekend":
    selected_pol = st.selectbox("Pilih Polutan", pollutants)
    weekday_avg = data_all_stations.groupby(['station', 'day_type'])[pollutants].mean().reset_index()

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(data=weekday_avg, x='station', y=selected_pol, hue='day_type', ax=ax)
    ax.set_title(f'Rata-rata {selected_pol} per Stasiun (Weekday vs Weekend)')
    ax.set_ylabel(f'{selected_pol} (µg/m³)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    for c in ax.containers:
        ax.bar_label(c, fmt='%.1f', label_type='edge', fontsize=8)

    st.pyplot(fig)

    st.markdown("""
    - Dongsi Station memiliki rata-rata PM2.5 tertinggi baik saat weekday maupun weekend.
    - Dingling Station memiliki rata-rata PM2.5 terendah pada kedua jenis hari tersebut.
    - Gucheng Station menunjukkan rata-rata PM10 tertinggi saat weekday dan weekend.
    - Dingling Station kembali menjadi stasiun dengan rata-rata PM10 terendah.
    - Wanliu Station memiliki rata-rata NO2 tertinggi di weekday dan weekend.
    - Dingling Station mencatatkan rata-rata NO2 terendah di kedua hari.
    - Saat weekday, stasiun dengan rata-rata SO2 tertinggi adalah Dongsi dan Nongzhanguan Station. Saat weekend, Nongzhanguan Station tetap menjadi yang tertinggi.
    - Dingling Station konsisten memiliki rata-rata SO2 terendah baik weekday maupun weekend.
    - Wanshouxigong Station memiliki rata-rata CO tertinggi pada weekday dan weekend.
    - Dingling Station mencatatkan rata-rata CO terendah di kedua periode.
    - Dingling Station justru menjadi stasiun dengan rata-rata O3 tertinggi saat weekday dan weekend.
    - Sebaliknya, Wanliu Station memiliki rata-rata O3 terendah di kedua jenis hari.""")
