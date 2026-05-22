import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA WARNA
# ==========================================
st.set_page_config(
    page_title="Giziku Anak - Panduan Sehat Ayah Bunda",
    page_icon="👦",
    layout="wide"
)

# Kustom CSS untuk nuansa ramah anak (Hijau Organik & Hangat)
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #2E7D32;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4CAF50;
        font-weight: bold;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #1B5E20 !important;
        border-bottom-color: #1B5E20 !important;
    }
    h1, h2, h3 {
        color: #1B5E20 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MEMUAT DATASET DARI GITHUB (OTOMATIS & AMAN)
# ==========================================
@st.cache_data
def load_all_data():
    # 2a. Memuat Data Gizi Makanan Anak dari GitHub Anda
    url_makanan = "https://github.com/C1nt4833/Dashboard-Giziku/blob/b1bd9d0b28260766d710132dc2ebf09632fcacfd/EDA_Data_Makanan_Anak(revisi).csv"
    df_makanan = pd.read_csv(url_makanan, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
    df_makanan.columns = df_makanan.columns.str.strip().str.replace('﻿', '')
    
    # Kunci nama kolom berdasarkan file revisi Anda
    mapping_kolom = {
        'Nama': 'Nama Makanan',
        'Kategori': 'Kelompok Makanan',
        'Takaran Porsi': 'Ukuran Porsi',
        'Kalori (kal)': 'Energi (Kalori)',
        'Protein (g)': 'Protein (Pertumbuhan)',
        'Karbohidrat (g)': 'Karbohidrat',
        'Lemak (g)': 'Lemak',
        'Gula (g)': 'Gula (Batasi)'
    }
    df_makanan = df_makanan.rename(columns=mapping_kolom)
    
    # Konversi kolom zat gizi utama menjadi angka murni
    kolom_gizi = ['Energi (Kalori)', 'Protein (Pertumbuhan)', 'Karbohidrat', 'Lemak', 'Gula (Batasi)']
    for col in kolom_gizi:
        if col in df_makanan.columns:
            if df_makanan[col].dtype == 'object':
                df_makanan[col] = df_makanan[col].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float)
            df_makanan[col] = pd.to_numeric(df_makanan[col], errors='coerce').fillna(0.0)
            
    # 2b. Memuat Data Standar AKG Kementerian Kesehatan
    url_akg = "https://raw.githubusercontent.com/C1nt4833/giziku-etl/main/akg_indonesia_final.csv"
    df_akg = pd.read_csv(url_akg, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
    df_akg.columns = df_akg.columns.str.strip().str.replace('﻿', '')
    
    return df_makanan, df_akg

try:
    df_makanan, df_akg = load_all_data()
except Exception as e:
    st.error(f"Gagal memuat data dari GitHub. Silakan periksa kembali repositori Anda. Info: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR: KONSULTASI PROFIL ANAK
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/children.png", width=75)
st.sidebar.title("💚 Profil Buah Hati")
st.sidebar.markdown("Tentukan usia dan jenis kelamin anak untuk menyesuaikan batas gizi hariannya.")

selected_gender = st.sidebar.radio("Jenis Kelamin Anak:", ['Laki-laki', 'Perempuan'])
selected_usia = st.sidebar.selectbox("Usia Anak Saat Ini:", ['Anak Sekolah (7-9 tahun)', 'Anak Sekolah (10-12 tahun)'])

# Filter data AKG
if '7-9' in selected_usia:
    df_akg_filtered = df_akg[(df_akg['Kategori'] == 'Bayi/Anak') & (df_akg['Label_Umur_Kondisi'].str.contains('7-9', na=False))]
else:
    kategori_target = 'Laki-Laki' if selected_gender == 'Laki-laki' else 'Perempuan'
    df_akg_filtered = df_akg[(df_akg['Kategori'] == kategori_target) & (df_akg['Label_Umur_Kondisi'].str.contains('10-12', na=False))]

# Mengambil batas angka kecukupan gizi
if not df_akg_filtered.empty:
    limit_energi = float(pd.to_numeric(df_akg_filtered['Energi (kkal)'].values[0], errors='coerce'))
    limit_protein = float(pd.to_numeric(df_akg_filtered['Protein (g)'].values[0], errors='coerce'))
else:
    limit_energi, limit_protein = 1650.0, 40.0

st.sidebar.markdown(f"""
<div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; font-size: 14px;">
<b style="color: #1B5E20;">🎯 Target Harian Ideal Anak:</b><br/>
• 🔋 <b>Tenaga Fisik:</b> {limit_energi:.0f} Kalori<br/>
• 🥩 <b>Tumbuh Kembang:</b> {limit_protein:.0f} gram Protein<br/>
• ⚠️ <b>Batas Aman Gula:</b> Maksimal 25 gram sehari
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN UTAMA: INTERFASE AYAH BUNDA
# ==========================================
st.title("👦 Kalkulator & Kamus Gizi Anak Sekolah (Usia 6-12 Tahun)")
st.markdown("Selamat datang Ayah & Bunda! Halaman ini membantu memantau apakah bekal sekolah, sarapan, atau jajanan harian si kecil sudah sehat atau justru mengandung gula berlebih.")
st.markdown("---")

# --- FITUR 1: KALKULATOR BEKAL & JAJANAN ---
st.header("🛒 Fitur 1: Hitung Gizi Makanan & Jajanan Hari Ini")
st.markdown("*Pilih makanan apa saja yang dimakan atau dijadikan bekal anak hari ini untuk melihat hasilnya:*")

nama_kolom_makanan = 'Nama Makanan' if 'Nama Makanan' in df_makanan.columns else df_makanan.columns[0]

pilihan_makanan_ortu = st.multiselect(
    "Pilih atau ketik nama makanan anak hari ini:",
    options=df_makanan[nama_kolom_makanan].unique(),
    default=[]
)

df_selected_menu = df_makanan[df_makanan[nama_kolom_makanan].isin(pilihan_makanan_ortu)]

if not df_selected_menu.empty:
    # Kalkulasi total zat gizi
    total_energi = float(df_selected_menu['Energi (Kalori)'].sum()) if 'Energi (Kalori)' in df_selected_menu.columns else 0.0
    total_protein = float(df_selected_menu['Protein (Pertumbuhan)'].sum()) if 'Protein (Pertumbuhan)' in df_selected_menu.columns else 0.0
    total_gula = float(df_selected_menu['Gula (Batasi)'].sum()) if 'Gula (Batasi)' in df_selected_menu.columns else 0.0
    
    pct_energi = (total_energi / limit_energi) * 100
    pct_protein = (total_protein / limit_protein) * 100
    
    # Tampilan Metrik Ringkas & Jelas untuk Orang Tua
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Energi Terpenuhi", f"{total_energi:.0f} Kalori", f"{pct_energi:.1f}% dari Kebutuhan")
    with col_m2:
        st.metric("Total Protein Anak", f"{total_protein:.1f} gram", f"{pct_protein:.1f}% dari Kebutuhan")
    with col_m3:
        # Indikator warna untuk gula
        status_gula = "⚠️ Tinggi Gula" if total_gula > 25 else "✅ Aman"
        st.metric("Total Konsumsi Gula", f"{total_gula:.1f} gram", f"Status: {status_gula}", delta_color="inverse" if total_gula > 25 else "normal")

    # Evaluasi Ringkas Berbahasa Awam
    st.markdown("#### 💡 Penilaian Nutrisi oleh Ahli Gizi:")
    if total_gula > 25:
        st.error("⚠️ **Waspada Bunda!** Gabungan jajanan ini mengandung gula melebihi **25 gram**. Terlalu banyak gula bisa membuat anak mudah lelah di kelas, sulit fokus, dan merusak gigi. Sebaiknya kurangi porsinya ya.")
    elif total_protein < (limit_protein * 0.25):
        st.warning("💡 **Tips Tumbuh Kembang:** Energi bekal sudah cukup baik, tapi kandungan **Proteinnya masih sedikit rendah**. Coba tambahkan lauk seperti telur rebus, potongan ayam, tahu, atau segelas susu murni agar pertumbuhan tinggi badannya maksimal.")
    else:
        st.success("✅ **Luar Biasa!** Kombinasi makanan ini sangat seimbang. Mengandung energi yang cukup untuk aktivitas belajarnya dan kadar gula yang terjaga dengan baik.")
else:
    st.info("Silakan pilih satu atau beberapa makanan di atas untuk melihat rapor gizi anak.")

st.markdown("---")

# --- FITUR 2: GRAFIK PEMAHAMAN JAJANAN ---
st.header("📊 Fitur 2: Panduan Memilih Jajanan Sehat")
tab_distribusi, tab_kategori = st.tabs(["📈 Cari Tahu Kelompok Makanan Ramah Anak", "🏭 Rata-Rata Kandungan Gizi"])

with tab_distribusi:
    st.subheader("Seberapa Banyak Kandungan Gula atau Kalori dalam Makanan Anak?")
    st.markdown("Gunakan grafik di bawah ini untuk melihat peta sebaran makanan. Semakin ke kanan balok grafik, berarti kandungan zat tersebut semakin tinggi.")
    
    pilihan_zat = st.selectbox(
        "Pilih Komponen yang Ingin Dilihat:",
        ['Energi (Kalori)', 'Protein (Pertumbuhan)', 'Gula (Batasi)'],
        key="sb_zat"
    )
    
    fig_hist = px.histogram(
        df_makanan,
        x=pilihan_zat,
        nbins=20,
        title=f"Grafik Jumlah Produk Makanan Berdasarkan Kandungan {pilihan_zat}",
        color_discrete_sequence=['#4CAF50'],
        labels={pilihan_zat: f"Jumlah Kandungan {pilihan_zat}"}
    )
    fig_hist.update_layout(plot_bgcolor='white', paper_bgcolor='white', yaxis_title="Banyaknya Jenis Makanan")
    st.plotly_chart(fig_hist, use_container_width=True)

with tab_kategori:
    st.subheader("Perbandingan Kandungan Gizi Antar Kelompok Makanan")
    st.markdown("Grafik ini membantu Bunda mengetahui kelompok jajanan mana yang paling padat energi, tinggi protein, atau justru paling manis (banyak gula).")
    
    if 'Kelompok Makanan' in df_makanan.columns:
        df_grouped = df_makanan.groupby('Kelompok Makanan')[['Energi (Kalori)', 'Protein (Pertumbuhan)', 'Gula (Batasi)']].mean().reset_index()
        pilihan_urut = st.radio("Urutkan Kelompok Makanan Berdasarkan:", ['Energi (Kalori)', 'Protein (Pertumbuhan)', 'Gula (Batasi)'], horizontal=True)
        df_grouped = df_grouped.sort_values(by=pilihan_urut, ascending=False)
        
        fig_bar = px.bar(
            df_grouped,
            x='Kelompok Makanan',
            y=pilihan_urut,
            color=pilihan_urut,
            title=f"Rata-rata Kandungan {pilihan_urut} per Kelompok Makanan",
            color_continuous_scale=['#E8F5E9', '#4CAF50', '#1B5E20'],
            labels={pilihan_urut: f"Rata-rata {pilihan_urut}"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Informasi Kelompok Makanan tidak ditemukan.")

# --- FITUR 3: KAMUS DATA DETAIL LENGKAP ---
st.markdown("---")
st.header("🔍 Fitur 3: Kamus Gizi Lengkap Aneka Makanan & Jajanan")
st.markdown("Cari tahu kandungan gizi lengkap dari makanan tertentu secara instan. Ketik nama makanan di bawah ini:")

pencarian_bunda = st.text_input("Ketik nama makanan di sini (Contoh: Popcorn, Permen, Biskuit):", value="", placeholder="Mulai mengetik...")

df_tabel_final = df_makanan.copy()
if pencarian_bunda and nama_kolom_makanan in df_tabel_final.columns:
    df_tabel_final = df_tabel_final[df_tabel_final[nama_kolom_makanan].str.contains(pencarian_bunda, case=False, na=False)]

kolom_tampil = [c for c in ['Nama Makanan', 'Kelompok Makanan', 'Ukuran Porsi', 'Energi (Kalori)', 'Protein (Pertumbuhan)', 'Karbohidrat', 'Lemak', 'Gula (Batasi)'] if c in df_tabel_final.columns]
st.dataframe(df_tabel_final[kolom_tampil].rename(columns={'Energi (Kalori)': 'Kalori (kal)', 'Protein (Pertumbuhan)': 'Protein (g)', 'Gula (Batasi)': 'Gula (g)'}), use_container_width=True)
