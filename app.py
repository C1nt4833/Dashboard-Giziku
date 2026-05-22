import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA WARNA
# ==========================================
st.set_page_config(
    page_title="Giziku Anak - Panduan Gizi Orang Tua",
    page_icon="👦",
    layout="wide"
)

# Kustom CSS untuk tema Hijau murni yang bersih
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #2E7D32;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4CAF50;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #2E7D32;
    }
    .stTabs [aria-selected="true"] {
        color: #1B5E20 !important;
        border-bottom-color: #1B5E20 !important;
    }
    h1, h2, h3 {
        color: #1B5E20 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MEMUAT DATA STANDAR AKG (TETAP DARI REPO BERBEDA)
# ==========================================
@st.cache_data
def load_akg_data():
    url_akg = "https://raw.githubusercontent.com/C1nt4833/giziku-etl/main/akg_indonesia_final.csv"
    df_akg = pd.read_csv(url_akg, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
    df_akg.columns = df_akg.columns.str.strip().str.replace('﻿', '')
    return df_akg

try:
    df_akg = load_akg_data()
except Exception as e:
    st.error(f"Gagal memuat data standar AKG: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR: PROFIL ANAK (FILTER AKG)
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/children.png", width=80)
st.sidebar.title("💚 Profil Buah Hati")
st.sidebar.markdown("Sesuaikan pilihan di bawah dengan profil anak Anda untuk melihat rekomendasi porsi.")

selected_gender = st.sidebar.radio("Jenis Kelamin Anak:", ['Laki-laki', 'Perempuan'])
selected_usia = st.sidebar.selectbox("Rentang Usia Anak:", ['Anak (7-9 tahun)', 'Anak (10-12 tahun)'])

# Logika filter mencocokkan struktur baris akg_indonesia_final.csv
if selected_usia == 'Anak (7-9 tahun)':
    df_akg_filtered = df_akg[
        (df_akg['Kategori'] == 'Bayi/Anak') & 
        (df_akg['Label_Umur_Kondisi'].str.contains('7-9', na=False))
    ]
else:
    kategori_target = 'Laki-Laki' if selected_gender == 'Laki-laki' else 'Perempuan'
    df_akg_filtered = df_akg[
        (df_akg['Kategori'] == kategori_target) & 
        (df_akg['Label_Umur_Kondisi'].str.contains('10-12', na=False))
    ]

# Ambil nilai limit AKG harian dan pastikan bertipe Float numeric murni
if not df_akg_filtered.empty:
    limit_energi = float(pd.to_numeric(df_akg_filtered['Energi (kkal)'].values[0], errors='coerce'))
    limit_protein = float(pd.to_numeric(df_akg_filtered['Protein (g)'].values[0], errors='coerce'))
    limit_karbo = float(pd.to_numeric(df_akg_filtered['Karbohidrat (g)'].values[0], errors='coerce'))
    limit_lemak = float(pd.to_numeric(df_akg_filtered['Lemak (g)'].values[0], errors='coerce'))
else:
    limit_energi, limit_protein, limit_karbo, limit_lemak = 1650.0, 40.0, 250.0, 55.0

# Box info kebutuhan harian anak di sidebar
st.sidebar.markdown(f"""
<div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32;">
<b style="color: #1B5E20;">🎯 Kebutuhan Harian Anak:</b><br/>
• 🔋 <b>Energi:</b> {limit_energi:.0f} kal<br/>
• 🥩 <b>Protein:</b> {limit_protein:.0f} g<br/>
• 🍞 <b>Karbohidrat:</b> {limit_karbo:.0f} g<br/>
• 🥑 <b>Lemak:</b> {limit_lemak:.0f} g
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN UTAMA DASHBOARD
# ==========================================
st.title("👦 Dashboard Giziku Anak Sekolah (Usia 6-12 Tahun)")
st.markdown("Membantu Ayah & Bunda memantau nutrisi makanan, bekal sekolah, dan jajanan harian anak demi tumbuh kembang yang optimal.")
st.markdown("---")

# --- WIDGET UPLOAD DATASET MAKANAN ---
st.subheader("📁 Langkah Awal: Unggah Dataset Makanan Anak")
uploaded_file = st.file_uploader("Pilih file CSV dataset makanan anak Anda (Contoh: EDA_Data_Makanan_Anak(revisi).csv)", type=["csv"])

if uploaded_file is not None:
    try:
        # Membaca file CSV yang diupload langsung oleh user
        df_makanan = pd.read_csv(uploaded_file, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
        df_makanan.columns = df_makanan.columns.str.strip().str.replace('﻿', '')
        
        # Bersihkan kolom gizi utama secara eksplisit agar menjadi float murni
        kolom_gizi = ['Kalori (kal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)']
        for col in kolom_gizi:
            if col in df_makanan.columns:
                if df_makanan[col].dtype == 'object':
                    df_makanan[col] = df_makanan[col].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float)
                df_makanan[col] = pd.to_numeric(df_makanan[col], errors='coerce').fillna(0.0)
        
        st.success("✅ Dataset makanan berhasil diunggah dan diproses!")
        
        st.markdown("---")

        # --- FITUR 1: SIMULASI MENU HARIAN ANAK ---
        st.header("🛒 Fitur 1: Simulasi Menu Makan & Jajanan Anak")
        st.markdown("*Bunda bisa memilih satu atau beberapa makanan yang dimakan anak hari ini untuk melihat pemenuhan gizinya.*")

        pilihan_makanan_ortu = st.multiselect(
            "Pilih makanan/jajanan yang dikonsumsi anak hari ini:",
            options=df_makanan['Nama'].unique() if 'Nama' in df_makanan.columns else df_makanan.iloc[:, 0].unique(),
            default=[]
        )

        df_selected_menu = df_makanan[df_makanan['Nama'].isin(pilihan_makanan_ortu)] if 'Nama' in df_makanan.columns else pd.DataFrame()

        if not df_selected_menu.empty:
            total_energi = float(df_selected_menu['Kalori (kal)'].sum()) if 'Kalori (kal)' in df_selected_menu.columns else 0.0
            total_protein = float(df_selected_menu['Protein (g)'].sum()) if 'Protein (g)' in df_selected_menu.columns else 0.0
            total_karbo = float(df_selected_menu['Karbohidrat (g)'].sum()) if 'Karbohidrat (g)' in df_selected_menu.columns else 0.0
            total_lemak = float(df_selected_menu['Lemak (g)'].sum()) if 'Lemak (g)' in df_selected_menu.columns else 0.0
            total_gula = float(df_selected_menu['Gula (g)'].sum()) if 'Gula (g)' in df_selected_menu.columns else 0.0
            
            pct_energi = (total_energi / limit_energi) * 100
            pct_protein = (total_protein / limit_protein) * 100
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Total Kalori Masuk", f"{total_energi:.1f} kal", f"{pct_energi:.1f}% Target")
            with col_m2:
                st.metric("Total Protein", f"{total_protein:.1f} g", f"{pct_protein:.1f}% Target")
            with col_m3:
                st.metric("Total Gula", f"{total_gula:.1f} g", "Batas anak: ~25g", delta_color="inverse")
            with col_m4:
                st.metric("Jumlah Item", f"{len(df_selected_menu)} Menu")

            st.markdown("#### 💡 Catatan & Evaluasi Gizi Bekal/Jajanan Anak:")
            if total_gula > 25:
                st.error("⚠️ **Peringatan Gula:** Jajanan pilihan mengandung gula tinggi (lebih dari 25 gram). Batasi konsumsi makanan manis lainnya hari ini ya Bun!")
            elif total_protein < (limit_protein * 0.3):
                st.warning("💡 **Saran Protein:** Jumlah protein menu ini masih agak rendah. Bunda bisa menambahkan lauk hewani seperti telur, ayam, atau segelas susu.")
            else:
                st.success("✅ **Bagus Sekali!** Kombinasi menu ini seimbang dan siap memberikan energi yang cukup untuk aktivitas belajarnya.")
        else:
            st.info("Silakan pilih satu atau lebih menu makanan di atas untuk memulai simulasi gizi anak.")

        st.markdown("---")

        # --- FITUR 2: BARIS TAB ANALISIS DISTRIBUSI ---
        st.header("📊 Fitur 2: Eksplorasi Kamus Data Gizi Makanan")
        tab_distribusi, tab_kategori = st.tabs(["📈 Analisis Kandungan Zat Gizi", "🏭 Perbandingan Kategori Makanan"])

        with tab_distribusi:
            st.subheader("Melihat Sebaran Nutrisi Jajanan Anak")
            pilihan_zat = st.selectbox(
                "Pilih Komponen Zat Gizi:",
                [c for c in ['Kalori (kal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)'] if c in df_makanan.columns],
                key="sb_zat"
            )
            
            fig_hist = px.histogram(
                df_makanan,
                x=pilihan_zat,
                nbins=25,
                title=f"Grafik Banyaknya Jenis Makanan Berdasarkan Kandungan {pilihan_zat}",
                color_discrete_sequence=['#4CAF50'],
                marginal="box"
            )
            fig_hist.update_layout(plot_bgcolor='white', paper_bgcolor='white', bargap=0.05)
            st.plotly_chart(fig_hist, use_container_width=True)

        with tab_kategori:
            st.subheader("Rata-Rata Kandungan Gizi Berdasarkan Kelompok/Kategori")
            
            if 'Kategori' in df_makanan.columns:
                kolom_numerik = [c for c in ['Kalori (kal)', 'Protein (g)', 'Gula (g)'] if c in df_makanan.columns]
                df_grouped = df_makanan.groupby('Kategori')[kolom_numerik].mean().reset_index()
                pilihan_urut = st.radio("Urutkan Grafik Berdasarkan:", kolom_numerik, horizontal=True)
                df_grouped = df_grouped.sort_values(by=pilihan_urut, ascending=False)
                
                fig_bar = px.bar(
                    df_grouped,
                    x='Kategori',
                    y=pilihan_urut,
                    color=pilihan_urut,
                    title=f"Rata-rata Kandungan {pilihan_urut} per Kategori Makanan",
                    color_continuous_scale=['#E8F5E9', '#4CAF50', '#1B5E20']
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Kolom 'Kategori' tidak ditemukan di dataset makanan.")

        # --- FITUR 3: KAMUS DATA DETAIL LENGKAP ---
        st.markdown("---")
        st.header("🔍 Fitur 3: Kamus Gizi Lengkap Anak")
        pencarian_bunda = st.text_input("Ketik Nama Jajanan/Makanan di sini:", value="", placeholder="Contoh: Alpukat, Permen, Popcorn...")

        df_tabel_final = df_makanan.copy()
        if pencarian_bunda and 'Nama' in df_tabel_final.columns:
            df_tabel_final = df_tabel_final[df_tabel_final['Nama'].str.contains(pencarian_bunda, case=False, na=False)]

        kolom_tampil = [c for c in ['Nama', 'Kategori', 'Takaran Porsi', 'Kalori (kal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)'] if c in df_tabel_final.columns]
        st.dataframe(df_tabel_final[kolom_tampil], use_container_width=True)

    except Exception as e:
        st.error(f"Gagal memproses file yang diunggah. Pastikan format file sesuai. Error: {e}")
else:
    st.info("💡 Silakan unggah file dataset gizi makanan anak Anda (`.csv`) di atas terlebih dahulu untuk memunculkan visualisasi dashboard.")
