import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(
    page_title="Simulasi Polarisasi Hukum Malus",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Header Styling */
    .header-container {
        background-color: #006994; /* Biru Laut */
        color: white;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 32px;
        font-weight: bold;
        margin: 0;
    }
    .header-subtitle {
        font-size: 16px;
        margin: 5px 0;
        font-weight: normal;
    }
    
    /* Card Container Styling */
    .card-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #006994;
        margin-bottom: 15px;
        border-bottom: 2px solid #006994;
        padding-bottom: 5px;
    }
    
    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 14px;
        border-top: 1px solid #e0e0e0;
        margin-top: 50px;
        background-color: #f9f9f9;
    }
    
    /* Info Box */
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #006994;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Simulasi Polarisasi dengan Hukum Malus</h1>
        <p class="header-subtitle">Dikembangkan oleh Felix Marcellino Henrikus, S.Si.</p>
        <p class="header-subtitle">Program Studi Magister Sains Data, UKSW Salatiga</p>
        <p class="header-subtitle">Untuk digunakan dalam pembelajaran Optika Gelombang di S1 Fisika, UKSW Salatiga</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<div class='card-container'><div class='card-title'>Konfigurasi Sumber Cahaya</div></div>", unsafe_allow_html=True)
    
    source_type = st.selectbox(
        "Jenis Sumber Cahaya",
        ["Cahaya Tak Terpolarisasi", "Cahaya Terpolarisasi"]
    )
    
    if source_type == "Cahaya Terpolarisasi":
        source_angle = st.number_input("Sudut Polarisasi Sumber (derajat)", 0, 359, 0)
    else:
        source_angle = 0  # Tidak relevan untuk tak terpolarisasi
        
    light_mode = st.selectbox(
        "Jenis Panjang Gelombang",
        ["Monokromatik", "Polikromatik"]
    )
    
    if light_mode == "Monokromatik":
        wavelength = st.slider("Panjang Gelombang (nm)", 380, 1100, 550)
        wl_label = f"{wavelength} nm"
    else:
        wavelength = 550  # Default untuk kalkulasi
        wl_label = "Spektrum Tampak (Polikromatik)"
        
    st.markdown("<div class='card-container'><div class='card-title'>Konfigurasi Sistem</div></div>", unsafe_allow_html=True)
    
    n_polarizers = st.slider("Jumlah Polaroid", 2, 6, 2)
    
    advanced_mode = st.checkbox("Mode Lanjutan: Pengukuran Konsentrasi (Aktivitas Optik)")
    
    concentration = 0.0
    path_length = 1.0
    specific_rotation = 0.0
    
    if advanced_mode:
        st.info("Mode Aktivitas Optik: Sampel larutan ditempatkan antar polaroid.")
        concentration = st.number_input("Konsentrasi Larutan (g/mL)", min_value=0.0, value=0.1, step=0.01)
        path_length = st.number_input("Panjang Sel (dm)", min_value=0.1, value=1.0, step=0.1)
        specific_rotation = st.number_input("Rotasi Spesifik [α] (derajat·mL/(g·dm))", min_value=0.0, value=66.5, step=0.1)

# --- MAIN LOGIC ---

st.markdown("<div class='card-container'><div class='card-title'>Parameter Sudut Polaroid</div></div>", unsafe_allow_html=True)

# Informasi sistem koordinat sudut
st.markdown("""
    <div class="info-box">
        <strong>Informasi Sistem Koordinat:</strong><br>
        • Sudut 0° mengarah ke <strong>vertikal atas</strong><br>
        • Peningkatan sudut berputar <strong>searah jarum jam</strong><br>
        • Rentang sudut: 0° - 359°
    </div>
""", unsafe_allow_html=True)

# Input sudut untuk setiap polaroid menggunakan number input
angles = []
cols = st.columns(n_polarizers)
for i in range(n_polarizers):
    with cols[i]:
        angle = st.number_input(
            f"Polaroid {i+1} (θ{i+1})",
            min_value=0,
            max_value=359,
            value=0 if i == 0 else 90,
            step=1,
            key=f"p{i}"
        )
        angles.append(angle)

# Perhitungan Intensitas
I0 = 100.0  # Intensitas Awal (Satuan Arbitrer)
intensities = [I0]
labels = ["Sumber"]
angles_effective = [source_angle if source_type == "Cahaya Terpolarisasi" else None]

current_intensity = I0
current_angle = source_angle if source_type == "Cahaya Terpolarisasi" else None

# Logika Fisika
for i in range(n_polarizers):
    theta_polarizer = angles[i]
    
    # Jika polaroid pertama dan cahaya tak terpolarisasi
    if i == 0 and source_type == "Cahaya Tak Terpolarisasi":
        current_intensity = 0.5 * current_intensity
        current_angle = theta_polarizer
    else:
        # Hitung selisih sudut
        if current_angle is None:
            # Kasus edge jika sebelumnya tak terpolarisasi tapi logic gagal (seharusnya tidak terjadi)
            delta_theta = 0
        else:
            delta_theta = np.radians(theta_polarizer - current_angle)
        
        # Hukum Malus
        current_intensity = current_intensity * (np.cos(delta_theta) ** 2)
        current_angle = theta_polarizer
    
    # Jika mode aktivitas optik aktif, tambahkan rotasi setelah melewati polaroid ini (sebelum ke berikutnya)
    # Asumsi: Larutan ditempatkan setelah polaroid ke-i (kecuali terakhir)
    rotation_angle = 0
    if advanced_mode and i < n_polarizers - 1:
        # Rumus: α = [α] * l * c
        rotation_angle = specific_rotation * path_length * concentration
        current_angle += rotation_angle # Rotasi bidang polarisasi
        
        # Catatan: Intensitas tidak berubah karena aktivitas optik ideal (hanya memutar bidang)
    
    intensities.append(current_intensity)
    labels.append(f"P{i+1}" + (f" + Larutan" if advanced_mode and i < n_polarizers - 1 else ""))
    angles_effective.append(current_angle)

# --- VISUALISASI DATA ---

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='card-container'><div class='card-title'>Grafik Intensitas Cahaya</div></div>", unsafe_allow_html=True)
    
    df = pd.DataFrame({
        "Tahap": labels,
        "Intensitas": intensities,
        "Sudut Efektif": [0 if x is None else x % 360 for x in angles_effective]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Tahap"], 
        y=df["Intensitas"], 
        mode="lines+markers", 
        name="Intensitas",
        line=dict(color="#006994", width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        height=400,
        xaxis_title="Tahap Polaroid",
        yaxis_title="Intensitas (Satuan Arbitrer)",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("<div class='card-container'><div class='card-title'>Hasil Pengukuran</div></div>", unsafe_allow_html=True)
    
    st.metric(label="Intensitas Awal", value=f"{I0:.2f}")
    st.metric(label="Intensitas Akhir", value=f"{intensities[-1]:.2f}")
    st.metric(label="Transmitansi Total", value=f"{(intensities[-1]/I0)*100:.2f} %")
    
    st.markdown("### Detail Panjang Gelombang")
    st.info(f"Mode: {light_mode}")
    t.info(f"Nilai: {wl_label}")
    
    if advanced_mode:
        st.markdown("### Parameter Larutan")
        st.write(f"**Rotasi Optik:** {specific_rotation * path_length * concentration:.2f}°")
        st.write(f"**Konsentrasi:** {concentration} g/mL")

# --- TABEL DATA ---
st.markdown("<div class='card-container'><div class='card-title'>Tabel Data Intensitas per Tahap</div></div>", unsafe_allow_html=True)
st.dataframe(df.style.format({"Intensitas": "{:.2f}", "Sudut Efektif": "{:.1f}°"}), use_container_width=True)

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        copyright ©2026 - Felix Marcellino Henrikus, S.Si. - UKSW Salatiga
    </div>
""", unsafe_allow_html=True)
