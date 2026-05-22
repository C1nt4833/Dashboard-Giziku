import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA WARNA (KUSTOM CSS)
# ==========================================
st.set_page_config(
    page_title="Giziku Anak - Panduan Gizi Orang Tua",
    page_icon="👦",
    layout="wide"
)

# Kustom CSS untuk memaksa tema warna dominan Hijau & Putih murni yang bersih
st.markdown("""
    <style>
    /* Mengubah warna latar belakang utama dan teks */
    .stApp {
        background-color: #FFFFFF;
        color: #2E7D32;
    }
    /* Mengubah gaya tombol dan navigasi */
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
# 2. MEMUAT DATASET (DENGAN CACHING)
# ==========================================
@st.cache_data
def load_all_data():
    # Data Gizi Makanan
    url_makanan = "https://raw.githubusercontent.com/ekasaaa/analisis-dataset-gizi/refs/heads/main/nilai-gizi.csv"
    df_makanan = pd.read_csv(url_makanan, sep=";")
    
    df_makanan.drop(df_makanan.columns[df_makanan.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    kolom_gizi = ['Energi (kkal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)']
    for col in kolom_gizi:
        if df_makanan[col].dtype == 'object':
            df_makanan[col] = df_makanan[col].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float)
            df_makanan[col] = df_makanan[col].fillna(df_makanan[col].median())
            
    # Data Standar AKG
    url_akg = "https://raw.githubusercontent.com/C1nt4833/giziku-etl/main/akg_indonesia_final.csv"
    df_akg = pd.read_csv(url_akg)
    
    # --- PEMBERSIHAN TOTAL NAMA KOLOM AKG (Membuang Spasi & Huruf Kecil Semua) ---
    # Langkah ini akan mengubah 'Jenis Kelamin' menjadi 'jeniskelamin' 
    # dan 'Kelompok Usia' menjadi 'kelompokusia' agar terhindar dari KeyError
    df_akg.columns = df_akg.columns.str.replace(' ', '').str.lower().str.strip()
    
    return df_makanan, df_akg

try:
    df_makanan, df_akg = load_all_data()
except Exception as e:
    st.error(f"Gagal memuat data dari GitHub: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR: PROFIL ANAK KHUSUS 6-12 TAHUN
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/children.png", width=80)
st.sidebar.title("💚 Profil Buah Hati")
st.sidebar.markdown("Sesuaikan pilihan di bawah dengan profil anak Anda untuk melihat rekomendasi porsi.")

# Menentukan pilihan input orang tua
list_gender = ['Laki-laki', 'Perempuan']
selected_gender = st.sidebar.radio("Jenis Kelamin Anak:", list_gender)

usia_anak_target = ['Anak (7-9 tahun)', 'Anak (10-12 tahun)']
selected_usia = st.sidebar.selectbox("Rentang Usia Anak:", usia_anak_target)

# Menerapkan filter berdasarkan nama kolom baru yang tanpa spasi sama sekali
df_akg_filtered = df_akg[
    (df_akg['jeniskelamin'].str.strip() == selected_gender) & 
    (df_akg['kelompokusia'].str.strip() == selected_usia)
]

# Ambil batasan nilai gizi secara dinamis dari kata kunci kolom yang dikecilkan
if not df_akg_filtered.empty:
    col_e = [c for c in df_akg.columns if 'energi' in c or 'kalori' in c][0]
    col_p = [c for c in df_akg.columns if 'protein' in c][0]
    col_k = [c for c in df_akg.columns if 'karbo' in c][0]
    col_l = [c for c in df_akg.columns if 'lemak' in c][0]
    
    limit_energi = float(df_akg_filtered[col_e].values[0])
    limit_protein = float(df_akg_filtered[col_p].values[0])
    limit_karbo = float(df_akg_filtered[col_k].values[0])
    limit_lemak = float(df_akg_filtered[col_l].values[0])
else:
    # Nilai standar default anak sekolah jika terjadi kegagalan filter data
    limit_energi, limit_protein, limit_karbo, limit_lemak = 1800.0, 45.0, 250.0, 55.0

# Tampilan Kuota Gizi Anak yang Bersih dan Berwarna Hijau Lembut
st.sidebar.markdown(f"""
<div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32;">
<b style="color: #1B5E20;">🎯 Kebutuhan Harian Anak:</b><br/>
• 🔋 <b>Energi:</b> {limit_energi:.0f} kkal<br/>
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

# --- FITUR INTERAKTIF UTAMA: PANDUAN MENU HARIAN ANAK ---
st.header("🛒 Fitur 1: Simulasi Menu Makan & Jajanan Anak")
st.markdown("*Bunda bisa memilih satu atau beberapa makanan yang dimakan anak hari ini untuk melihat apakah gizinya sudah tercukupi atau justru berlebihan.*")

pilihan_makanan_ortu = st.multiselect(
    "Pilih makanan/jajanan yang dikonsumsi anak hari ini:",
    options=df_makanan['Nama_Makanan'].unique(),
    default=[df_makanan['Nama_Makanan'].iloc[0]] if len(df_makanan) > 0 else None
)

df_selected_menu = df_makanan[df_makanan['Nama_Makanan'].isin(pilihan_makanan_ortu)]

if not df_selected_menu.empty:
    total_energi = df_selected_menu['Energi (kkal)'].sum()
    total_protein = df_selected_menu['Protein (g)'].sum()
    total_karbo = df_selected_menu['Karbohidrat (g)'].sum()
    total_lemak = df_selected_menu['Lemak (g)'].sum()
    total_gula = df_selected_menu['Gula (g)'].sum()
    
    pct_energi = (total_energi / limit_energi) * 100
    pct_protein = (total_protein / limit_protein) * 100
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Kalori Masuk", f"{total_energi:.1f} kkal", f"{pct_energi:.1f}% Kebutuhan Harian")
    with col_m2:
        st.metric("Total Protein", f"{total_protein:.1f} g", f"{pct_protein:.1f}% Kebutuhan Harian")
    with col_m3:
        st.metric("Total Gula Dikonsumsi", f"{total_gula:.1f} g", "Batas anak: ~25g/hari", delta_color="inverse")
    with col_m4:
        st.metric("Jumlah Item Makanan", f"{len(df_selected_menu)} Menu")

    st.markdown("#### 💡 Catatan & Evaluasi Gizi Bekal/Jajanan Anak:")
    if total_gula > 25:
        st.error("⚠️ **Peringatan Gula:** Makanan yang dipilih mengandung gula tinggi (lebih dari 25 gram). Kurangi jajanan manis hari ini untuk mencegah anak terlalu hiperaktif dan menjaga kesehatan gigi!")
    elif total_protein < (limit_protein * 0.3):
        st.warning("💡 **Saran Protein:** Kandungan protein dari menu ini masih agak rendah untuk anak usia pertumbuhan. Bunda bisa menambahkan telur, susu, atau keju pada bekalnya.")
    else:
        st.success("✅ **Bagus Sekali!** Kombinasi menu ini memberikan sebaran gizi dan protein yang baik untuk mendukung aktivitas sekolah dan belajar anak hari ini.")
else:
    st.info("Silakan pilih minimal satu menu makanan di atas untuk memulai simulasi pemenuhan gizi anak.")

st.markdown("---")

# --- BARIS TAB UNTUK ANALISIS MENDALAM ---
st.header("📊 Fitur 2: Eksplorasi Kamus Data Gizi Makanan")
tab_distribusi, tab_produsen = st.tabs(["📈 Analisis Kandungan Zat Gizi", "🏭 Perbandingan Kategori & Produsen"])

with tab_distribusi:
    st.subheader("Melihat Sebaran Nutrisi Makanan di Indonesia")
    pilihan_zat = st.selectbox(
        "Pilih Komponen Zat Gizi:",
        ['Energi (kkal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)']
    )
    
    fig_hist = px.histogram(
        df_makanan,
        x=pilihan_zat,
        nbins=30,
        title=f"Grafik Banyaknya Makanan Berdasarkan Kandungan {pilihan_zat}",
        color_discrete_sequence=['#4CAF50'],
        marginal="box"
    )
    fig_hist.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        bargap=0.05
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab_produsen:
    st.subheader("Rata-Rata Kandungan Gizi Berdasarkan Kelompok / Produsen")
    top_p_idx = df_makanan['Produsen'].value_counts().head(10).index
    df_top_p = df_makanan[df_makanan['Produsen'].isin(top_p_idx)]
    df_grouped_p = df_top_p.groupby('Produsen')[['Energi (kkal)', 'Protein (g)', 'Gula (g)']].mean().reset_index()
    
    pilihan_urut = st.radio("Urutkan Produsen Berdasarkan Rerata:", ['Energi (kkal)', 'Protein (g)', 'Gula (g)'], horizontal=True)
    df_grouped_p = df_grouped_p.sort_values(by=pilihan_urut, ascending=False)
    
    fig_bar = px.bar(
        df_grouped_p,
        x='Produsen',
        y=pilihan_urut,
        color=pilihan_urut,
        title=f"Rata-rata {pilihan_urut} per Kategori Produsen",
        color_continuous_scale=['#E8F5E9', '#4CAF50', '#1B5E20']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- FITUR 3: TABEL DATA DETAIL LENGKAP ---
st.markdown("---")
st.header("🔍 Fitur 3: Kamus Gizi Lengkap (Bisa Dicari)")
pencarian_bunda = st.text_input("Ketik Nama Makanan di Sini untuk Mencari:", value="", placeholder="Contoh: Susu, Cokelat, Nasi...")

df_tabel_final = df_makanan.copy()
if pencarian_bunda:
    df_tabel_final = df_tabel_final[df_tabel_final['Nama_Makanan'].str.contains(pencarian_bunda, case=False, na=False)]

kolom_ortu = ['Nama_Makanan', 'Produsen', 'Porsi', 'Energi (kkal)', 'Protein (g)', 'Karbohidrat (g)', 'Lemak (g)', 'Gula (g)']
st.dataframe(df_tabel_final[kolom_ortu], use_container_width=True)
