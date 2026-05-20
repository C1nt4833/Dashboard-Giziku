import streamlit as strl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# KONFIGURASI HALAMAN DASHBOARD
# ==========================================
strl.set_page_config(
    page_title="Dashboard Analisis Gizi & AKG",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set style visualisasi agar serasi dengan Streamlit (Dark/Light mode adaptive)
sns.set_theme(style="whitegrid")

# ==========================================
# LOAD DATASET (DENGAN CACHING AGAR CEPAT)
# ==========================================
@strl.cache_data
def load_data_makanan():
    try:
        return pd.read_csv('EDA_Data_Makanan_Anak.csv')
    except:
        return None

@strl.cache_data
def load_data_akg():
    try:
        return pd.read_csv('dataset_akg_final.csv')
    except:
        return None

df_makanan = load_data_makanan()
df_akg = load_data_akg()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
strl.sidebar.title("📌 Menu Navigasi")
menu_pilihan = strl.sidebar.radio(
    "Pilih Menu Analisis:",
    ["Halaman Utama / Beranda", "1. Dashboard Makanan Anak", "2. Dashboard Standar AKG"]
)

strl.sidebar.markdown("---")
strl.sidebar.markdown("💡 *Tips: Gunakan filter di setiap halaman untuk melihat data secara spesifik.*")

# ==========================================
# HALAMAN 1: BERANDA
# ==========================================
if menu_pilihan == "Halaman Utama / Beranda":
    strl.title("📊 Platform Dashboard Analisis Gizi & Kebutuhan AKG")
    strl.subheader("Selamat Datang di Aplikasi Dashboard Interaktif")
    
    strl.write("""
    Aplikasi ini dirancang untuk menyajikan visualisasi data hasil Exploratory Data Analysis (EDA) secara interaktif. 
    Terdapat dua fokus utama analisis yang dapat Anda jelajahi melalui menu di samping kiri:
    """)
    
    col1, col2 = strl.columns(2)
    with col1:
        strl.info("### 🥦 1. Dashboard Makanan Anak\nFokus pada profil nutrisi produk makanan anak, mendeteksi kandungan gula/kalori ekstrem, korelasi zat gizi, dan variasi distribusinya.")
    with col2:
        strl.success("### 📋 2. Dashboard Standar AKG\nFokus pada pola kebutuhan gizi harian (Energi, Protein, Lemak, Karbohidrat) berdasarkan kelompok demografis (Usia & Jenis Kelamin) di Indonesia.")

# ==========================================
# HALAMAN 2: DASHBOARD MAKANAN ANAK
# ==========================================
elif menu_pilihan == "1. Dashboard Makanan Anak":
    if df_makanan is None:
        strl.error("Gagal memuat file 'EDA_Data_Makanan_Anak.csv'. Pastikan file berada di folder yang sama dengan script ini.")
    else:
        strl.title("🥦 Dashboard Analisis Nutrisi Makanan Anak")
        
        # --- FILTER INTERAKTIF ---
        strl.markdown("### 🎛️ Filter Data")
        list_kategori = ["Semua Kategori"] + list(df_makanan['Kategori'].unique())
        pilihan_kategori = strl.selectbox("Pilih Kategori Makanan:", list_kategori)
        
        # Filter Data Berdasarkan Pilihan Pengguna
        if pilihan_kategori == "Semua Kategori":
            df_filtered = df_makanan
        else:
            df_filtered = df_makanan[df_makanan['Kategori'] == pilihan_kategori]
            
        # Ringkasan KPI Cards
        col_kpi1, col_kpi2, col_kpi3 = strl.columns(3)
        col_kpi1.metric("Total Sampel Makanan", f"{df_filtered.shape[0]} Produk")
        col_kpi2.metric("Rata-rata Kalori", f"{df_filtered['Kalori (kal)'].mean():.1f} kal")
        col_kpi3.metric("Rata-rata Gula", f"{df_filtered['Gula (g)'].mean():.1f} g")
        
        strl.markdown("---")
        
        # --- PERTANYAAN 1 & 2 (Dua Kolom) ---
        col_graph1, col_graph2 = strl.columns(2)
        
        with col_graph1:
            strl.subheader("📌 Top 10 Makanan Kalori Tertinggi")
            top_kalori = df_filtered.nlargest(10, 'Kalori (kal)')
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=top_kalori, x='Kalori (kal)', y='Nama', palette='Reds_r', ax=ax)
            ax.set_xlabel("Kalori (kal)")
            ax.set_ylabel("")
            strl.pyplot(fig)
            
        with col_graph2:
            strl.subheader("📌 Rata-rata Gula Per Kategori")
            # Tetap gunakan df_makanan global untuk perbandingan kategori yang adil
            rata_gula = df_makanan.groupby('Kategori')['Gula (g)'].mean().sort_values(ascending=False).reset_index()
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=rata_gula, x='Gula (g)', y='Kategori', palette='YlOrBr_r', ax=ax)
            ax.set_xlabel("Rata-rata Gula (gram)")
            ax.set_ylabel("")
            strl.pyplot(fig)

        strl.markdown("---")
        
        # --- PERTANYAAN 3 & 4 (Dua Kolom) ---
        col_graph3, col_graph4 = strl.columns(2)
        
        with col_graph3:
            strl.subheader("📌 Korelasi Hubungan Lemak vs Kalori")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.regplot(data=df_filtered, x='Lemak (g)', y='Kalori (kal)', color='teal', ax=ax)
            ax.set_xlabel("Lemak (gram)")
            ax.set_ylabel("Kalori (kal)")
            strl.pyplot(fig)
            # Tampilkan koefisien korelasi angka
            korelasi = df_filtered[['Lemak (g)', 'Kalori (kal)']].corr().iloc[0, 1]
            strl.caption(f"Nilai Koefisien Korelasi Pearson (r) = **{korelasi:.2f}**")
            
        with col_graph4:
            strl.subheader("📌 Analisis Variasi Nilai Gizi (CV)")
            kolom_nutrisi = ['Kalori (kal)', 'Protein (g)', 'Lemak (g)', 'Karbohidrat (g)', 'Gula (g)', 'Kolesterol (g)', 'Sodium (g)', 'Kalium (g)']
            cv_nutrisi = (df_filtered[kolom_nutrisi].std() / df_filtered[kolom_nutrisi].mean()).sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(x=cv_nutrisi.values, y=cv_nutrisi.index, palette='plasma', ax=ax)
            ax.set_xlabel("Nilai Standar Coefficient of Variation (CV)")
            strl.pyplot(fig)
            
        # --- LIHAT TABEL DATA MENTAH ---
        strl.markdown("---")
        with strl.expander("📄 Lihat Data Hasil Saringan"):
            strl.dataframe(df_filtered)

# ==========================================
# HALAMAN 3: DASHBOARD STANDAR AKG
# ==========================================
elif menu_pilihan == "2. Dashboard Standar AKG":
    if df_akg is None:
        strl.error("Gagal memuat file 'dataset_akg_final.csv'. Pastikan file berada di folder yang sama dengan script ini.")
    else:
        strl.title("📋 Dashboard Pola Kebutuhan Gizi Harian (AKG Indonesia)")
        
        # --- FILTER INTERAKTIF DEMOGRAFIS ---
        strl.markdown("### 🎛️ Filter Demografis")
        col_f1, col_f2 = strl.columns(2)
        with col_f1:
            pilihan_jk = strl.selectbox("Pilih Jenis Kelamin:", ["Semua", "Laki-laki", "Perempuan"])
        with col_f2:
            pilihan_gizi = strl.selectbox("Pilih Parameter Gizi Utama:", ["Energi (kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"])
            
        # Terapkan filter Jenis Kelamin
        if pilihan_jk == "Semua":
            df_akg_filtered = df_akg
        else:
            df_akg_filtered = df_akg[df_akg['Jenis Kelamin'] == pilihan_jk]
            
        strl.markdown("---")
        
        # --- VISUALISASI UTAMA: POLA KEBUTUHAN GIZI ANTAR KELOMPOK UMUR ---
        strl.subheader(f"📈 Pola Standar Kebutuhan Kebutuhan {pilihan_gizi} Berdasarkan Kelompok Usia")
        
        fig, ax = plt.subplots(figsize=(12, 5))
        # Menggunakan lineplot atau barplot berdasarkan kelompok umur
        sns.barplot(data=df_akg_filtered, x='Kelompok Umur', y=pilihan_gizi, hue='Jenis Kelamin' if pilihan_jk == "Semua" else None, palette='muted', ax=ax)
        plt.xticks(rotation=45, ha='right')
        ax.set_ylabel(pilihan_gizi)
        ax.set_xlabel("Kelompok Umur / Demografis")
        strl.pyplot(fig)
        
        strl.markdown("---")
        
        # --- ANALISIS PEMENUHAN GIZI (ASUPAN AKTUAL VS STANDAR AKG) ---
        strl.subheader("🎯 Analisis Gap Pemenuhan Gizi Masyarakat")
        strl.write("Bagian ini membandingkan apakah rata-rata asupan gizi harian aktual riil di lapangan sudah memenuhi standar AKG resmi.")
        
        # Catatan: Asumsi di dataset AKG Anda ada kolom asupan aktual atau Anda ingin menunjukkan summary tingkat pemenuhan gizi.
        # Jika ada kolom 'Asupan_Energi', kita bisa membuat visualisasi perbandingan (Grouped Bar Chart).
        kolom_aktual = f"Asupan {pilihan_gizi}"
        
        if kolom_aktual in df_akg.columns:
            # Jika kolom pembanding aktual tersedia di dataset Anda
            df_melted = df_akg_filtered.melt(id_vars=['Kelompok Umur'], value_vars=[pilihan_gizi, kolom_aktual], 
                                             var_name='Jenis Nilai', value_name='Nilai Gizi')
            
            fig2, ax2 = plt.subplots(figsize=(12, 5))
            sns.barplot(data=df_melted, x='Kelompok Umur', y='Nilai Gizi', hue='Jenis Nilai', palette='Set2', ax=ax2)
            plt.xticks(rotation=45, ha='right')
            strl.pyplot(fig2)
        else:
            # Jika data asupan aktual belum digabung, tampilkan placeholder simulasi/petunjuk analisis gap
            strl.warning(f"Untuk mengaktifkan grafik perbandingan otomatis, pastikan dataset Anda memiliki kolom asupan riil lapangan bernama 'Asupan {pilihan_gizi}'.")
            
            # Simulasi Insight Gizi Fisiologis
            strl.info("""
            **💡 Insight Pola Demografis & Fisiologis Standar AKG:**
            1. **Puncak Kebutuhan Energi & Makro:** Berada pada kelompok remaja akhir dan dewasa muda (usia 16-29 tahun), terutama pada laki-laki akibat aktivitas fisik dan pertumbuhan biologis makro.
            2. **Kelompok Kondisi Fisiologis Khusus:** Ibu hamil dan menyusui membutuhkan booster/tambahan energi (+300 hingga +500 kkal) serta protein lebih tinggi di atas standar wanita umum untuk mendukung tumbuh kembang janin.
            """)
            
        # --- LIHAT TABEL DATA AKG MENTAH ---
        with strl.expander("📄 Lihat Tabel Standar AKG Lengkap"):
            strl.dataframe(df_akg_filtered)
