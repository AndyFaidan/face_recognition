import streamlit as st
import cv2
import face_recognition as frg
import yaml
from utils import recognize, build_dataset

# Path: code\app.py
st.set_page_config(layout="wide")

# Configuration
cfg = yaml.load(open('config.yaml','r'), Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Pengaturan")

# Create menu bar
menu = ["Foto", "Webcam"]
pilihan = st.sidebar.selectbox("Jenis Input", menu)

# Slide to adjust tolerance
TOLERANCE = st.sidebar.slider("Toleransi", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Toleransi adalah ambang batas untuk pengenalan wajah. Semakin rendah toleransinya, semakin ketat pengenalan wajahnya. Semakin tinggi toleransinya, semakin longgar pengenalan wajahnya.")

# Information Section
st.sidebar.title("Informasi Mahasiswa")
nama_container = st.sidebar.empty()
nim_container = st.sidebar.empty()
nama_container.info('Nama: Tidak Diketahui')
nim_container.success('NIM: Tidak Diketahui')

if pilihan == "Foto":
    st.title("Aplikasi Pengenalan Wajah")
    st.write(PICTURE_PROMPT)
    foto_diunggah = st.file_uploader("Unggah", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

    if foto_diunggah:
        # Read the uploaded image with face_recognition
        for gambar in foto_diunggah:
            gambar = frg.load_image_file(gambar)
            gambar, nama, nim = recognize(gambar, TOLERANCE)
            nama_container.info(f"Nama: {nama}")
            nim_container.success(f"NIM: {nim}")
            st.image(gambar)
    else:
        st.info("Mohon unggah sebuah gambar")

elif pilihan == "Webcam":
    st.title("Aplikasi Pengenalan Wajah")
    st.write(WEBCAM_PROMPT)

    # Camera Setup
    kamera = cv2.VideoCapture(1)
    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_WINDOW = st.image([])

    while True:
        # Capture frame from the camera
        berhasil, bingkai = kamera.read()

        if not berhasil:
            st.error("Gagal mengambil bingkai dari kamera")
            st.info("Harap matikan aplikasi lain yang menggunakan kamera dan restart aplikasi")
            st.stop()

        # Process the frame for face recognition
        gambar, nama, nim = recognize(bingkai, TOLERANCE)
        gambar = cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB)

        # Display the name and NIM of the person
        nama_container.info(f"Nama: {nama}")
        nim_container.success(f"NIM: {nim}")

        # Display the frame with Streamlit
        FRAME_WINDOW.image(gambar, channels="RGB")

with st.sidebar.form(key='my_form'):
    st.title("Bagian Pengembang")
    tombol_submit = st.form_submit_button(label='MENYUSUN KEMBALI DATASET')
    if tombol_submit:
        with st.spinner("Menyusun kembali dataset..."):
            build_dataset()
        st.success("Dataset telah disusun ulang")
