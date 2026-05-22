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
# 2. MEMUAT DATASET UTAMA DARI GITHUB ANDA
# ==========================================
@st.cache_data
def load_all_data():
    # Tautan langsung (Raw Link) ke dataset Dashboard-Giziku Anda
    url_makanan = "https://raw.githubusercontent.com/C1nt4833/Dashboard-Giziku/main/EDA_Data_Makanan_Anak(revisi).csv"
    
    df_makanan = pd.read_csv(url_makanan, sep=',', encoding='utf-8-sig')
    df_makanan.columns = df_makanan.columns.str.strip().str.replace('﻿', '')
    
    # Konversi kolom zat gizi utama menjadi angka murni (float) demi keamanan kalkulasi
    kolom_gizi = ['Kalori (kal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)']
    for col in kolom_gizi:
        if col in df_makanan.columns:
            df_makanan[col] = pd.to_numeric(df_makanan[col], errors='coerce').fillna(0.0)
            
    # Memuat Data Standar AKG Kementerian Kesehatan
    url_akg = "https://raw.githubusercontent.com/C1nt4833/giziku-etl/main/akg_indonesia_final.csv"
    df_akg = pd.read_csv(url_akg, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
    df_akg.columns = df_akg.columns.str.strip().str.replace('﻿', '')
    
    return df_makanan, df_akg

try:
    df_makanan, df_akg = load_all_data()
except Exception as e:
    st.error(f"Gagal memuat data dari GitHub. Silakan periksa kembali sinkronisasi file Anda. Info Error: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR: KONSULTASI PROFIL ANAK
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/children.png", width=75)
st.sidebar.title("💚 Profil Buah Hati")
st.sidebar.markdown("Tentukan rentang usia dan jenis kelamin si kecil untuk menyesuaikan target batas gizi harian mereka.")

selected_gender = st.sidebar.radio("Jenis Kelamin Anak:", ['Laki-laki', 'Perempuan'])
selected_usia = st.sidebar.selectbox("Usia Anak Saat Ini:", ['Anak Sekolah (7-9 tahun)', 'Anak Sekolah (10-12 tahun)'])

# Logika pencocokan batas AKG otomatis
if '7-9' in selected_usia:
    df_akg_filtered = df_akg[(df_akg['Kategori'] == 'Bayi/Anak') & (df_akg['Label_Umur_Kondisi'].str.contains('7-9', na=False))]
else:
    kategori_target = 'Laki-Laki' if selected_gender == 'Laki-laki' else 'Perempuan'
    df_akg_filtered = df_akg[(df_akg['Kategori'] == kategori_target) & (df_akg['Label_Umur_Kondisi'].str.contains('10-12', na=False))]

if not df_akg_filtered.empty:
    limit_energi = float(pd.to_numeric(df_akg_filtered['Energi (kkal)'].values[0], errors='coerce'))
    limit_protein = float(pd.to_numeric(df_akg_filtered['Protein (g)'].values[0], errors='coerce'))
else:
    limit_energi, limit_protein = 1650.0, 40.0

st.sidebar.markdown(f"""
<div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; font-size: 14px;">
<b style="color: #1B5E20;">🎯 Target Harian Ideal Anak:</b><br/>
• 🔋 <b>Tenaga Fisik (Kalori):</b> {limit_energi:.0f} kal<br/>
• 🥩 <b>Tumbuh Kembang (Protein):</b> {limit_protein:.0f} g<br/>
• ⚠️ <b>Batas Aman Gula:</b> Maksimal 25g sehari
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN UTAMA: ANTARMUKA ORANG TUA
# ==========================================
st.title("👦 Kalkulator & Kamus Gizi Anak Sekolah (Usia 6-12 Tahun)")
st.markdown("Selamat datang Ayah & Bunda! Dashboard ini dirancang khusus untuk memantau apakah menu sarapan, bekal sekolah, atau jajanan harian si kecil sudah sehat seimbang atau justru mengandung gula berlebih.")
st.markdown("---")

# --- FITUR 1: KALKULATOR MENU HARIAN ---
st.header("🛒 Hitung Porsi & Gizi Jajanan Hari Ini")
st.markdown("*Pilih satu atau beberapa makanan yang dikonsumsi anak hari ini untuk melihat apakah energinya cukup:*")

pilihan_makanan_ortu = st.multiselect(
    "Pilih atau ketik nama makanan/jajanan anak:",
    options=df_makanan['Nama'].unique(),
    default=[]
)

df_selected_menu = df_makanan[df_makanan['Nama'].isin(pilihan_makanan_ortu)]

if not df_selected_menu.empty:
    # Menghitung total zat gizi berdasarkan pilihan orang tua
    total_energi = float(df_selected_menu['Kalori (kal)'].sum())
    total_protein = float(df_selected_menu['Protein (g)'].sum())
    total_gula = float(df_selected_menu['Gula (g)'].sum())
    
    pct_energi = (total_energi / limit_energi) * 100
    pct_protein = (total_protein / limit_protein) * 100
    
    # Tampilan Indikator Sederhana (Metrik) yang Mudah Dimengerti
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Tenaga Fisik Terpenuhi", f"{total_energi:.0f} Kalori", f"{pct_energi:.1f}% Kebutuhan")
    with col_m2:
        st.metric("Nutrisi Tumbuh Kembang", f"{total_protein:.1f} gram Protein", f"{pct_protein:.1f}% Kebutuhan")
    with col_m3:
        status_gula = "⚠️ Bahaya (Kelebihan)" if total_gula > 25 else "✅ Aman"
        st.metric("Total Konsumsi Gula", f"{total_gula:.1f} gram", f"Status: {status_gula}", delta_color="inverse" if total_gula > 25 else "normal")

    st.markdown("#### 💡 Penilaian Kesehatan Menu Pilihan Bunda:")
    if total_gula > 25:
        st.error("⚠️ **Waspada Bunda!** Gabungan jajanan ini mengandung gula tinggi melebihi **25 gram**. Terlalu banyak konsumsi gula bisa membuat anak mudah mengantuk/lemas di kelas, sulit fokus belajar, dan memicu karies gigi. Yuk, batasi atau ganti dengan buah potong segar!")
    elif total_protein < (limit_protein * 0.25):
        st.warning("💡 **Tips Pertumbuhan:** Total energi makanan sudah cukup, tetapi kandungan **Proteinnya masih agak rendah**. Coba selipkan lauk protein seperti telur dadar, potongan daging ayam, keju, atau segelas susu agar tinggi badan anak berkembang optimal.")
    else:
        st.success("✅ **Luar Biasa!** Pilihan makanan si kecil hari ini sangat seimbang. Energinya pas untuk beraktivitas di sekolah dan kadar gulanya aman terjaga.")
else:
    st.info("Silakan pilih satu atau beberapa makanan di atas untuk melihat rapor gizi jajanan anak.")

st.markdown("---")

# --- FITUR 2: GRAFIK PANDUAN JAJANAN SEHAT ---
st.header("📊 Panduan Memilih Kelompok Jajanan Sehat")
tab_distribusi, tab_kategori = st.tabs(["📈 Analisis Sebaran Zat Gizi", "🏭 Perbandingan Kategori Makanan"])

with tab_distribusi:
    st.subheader("Mengetahui Kadar Gula dan Protein Makanan")
    st.markdown("Gunakan grafik interaktif di bawah ini untuk melihat sebaran komponen gizi makanan anak. Semakin ke kanan letak baloknya, kandungan zat tersebut semakin tinggi.")
    
    pilihan_zat = st.selectbox(
        "Pilih Komponen Zat Gizi:",
        ['Kalori (kal)', 'Protein (g)', 'Gula (g)'],
        key="sb_zat"
    )
    
    # Pemetaan istilah teknis ke bahasa sederhana di judul grafik
    nama_ramah = "Energi (Kalori)" if pilihan_zat == 'Kalori (kal)' else ("Protein (Pertumbuhan)" if pilihan_zat == 'Protein (g)' else "Kadar Gula")
    
    fig_hist = px.histogram(
        df_makanan,
        x=pilihan_zat,
        nbins=20,
        title=f"Grafik Jumlah Jenis Makanan Berdasarkan Kandungan {nama_ramah}",
        color_discrete_sequence=['#4CAF50'],
        labels={pilihan_zat: f"Kandungan {nama_ramah}"}
    )
    fig_hist.update_layout(plot_bgcolor='white', paper_bgcolor='white', yaxis_title="Banyaknya Macam Makanan")
    st.plotly_chart(fig_hist, use_container_width=True)

with tab_kategori:
    st.subheader("Kelompok Makanan Mana yang Paling Sehat?")
    st.markdown("Grafik ini membantu Bunda mengetahui kategori makanan mana yang rata-rata paling tinggi energinya atau yang justru menimbun paling banyak gula.")
    
    if 'Kategori' in df_makanan.columns:
        df_grouped = df_makanan.groupby('Kategori')[['Kalori (kal)', 'Protein (g)', 'Gula (g)']].mean().reset_index()
        pilihan_urut = st.radio("Urutkan Grafik Berdasarkan:", ['Kalori (kal)', 'Protein (g)', 'Gula (g)'], horizontal=True)
        df_grouped = df_grouped.sort_values(by=pilihan_urut, ascending=False)
        
        fig_bar = px.bar(
            df_grouped,
            x='Kategori',
            y=pilihan_urut,
            color=pilihan_urut,
            title=f"Rata-rata Kandungan {pilihan_urut} per Kategori Makanan",
            color_continuous_scale=['#E8F5E9', '#4CAF50', '#1B5E20'],
            labels={pilihan_urut: f"Rata-rata {pilihan_urut}"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Kolom 'Kategori' tidak ditemukan di dataset makanan.")

# --- FITUR 3: KAMUS DETAIL LENGKAP ---
st.markdown("---")
st.header("🔍 Kamus Gizi Lengkap Makanan Anak")
st.markdown("Bunda ingin tahu kandungan gizi detail dari suatu makanan? Cukup ketik namanya di bawah ini:")

pencarian_bunda = st.text_input("Ketik nama makanan di sini (Contoh: Biskuit, Susu, Pisang):", value="", placeholder="Cari makanan...")

df_tabel_final = df_makanan.copy()
if pencarian_bunda and 'Nama' in df_tabel_final.columns:
    df_tabel_final = df_tabel_final[df_tabel_final['Nama'].str.contains(pencarian_bunda, case=False, na=False)]

# Tampilkan kolom dengan nama standar yang bersih sesuai file revisi Anda
kolom_tampil = ['Nama', 'Kategori', 'Takaran Porsi', 'Kalori (kal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)']
st.dataframe(df_tabel_final[kolom_tampil], use_container_width=True)
