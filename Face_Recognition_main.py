import streamlit as st
import cv2
import face_recognition as frg
import yaml
from utils import recognize, build_dataset

# Path: code\app.py
st.set_page_config(layout="wide")

# Configuration
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Pengaturan")

# Slide to adjust tolerance
TOLERANCE = st.sidebar.slider("Toleransi", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Toleransi adalah ambang batas untuk pengenalan wajah. Semakin rendah toleransinya, semakin ketat pengenalan wajahnya. Semakin tinggi toleransinya, semakin longgar pengenalan wajahnya.")

# Information Section
st.sidebar.title("Informasi Mahasiswa")
nama_container = st.sidebar.empty()
nim_container = st.sidebar.empty()
nama_container.info('Nama: Tidak Diketahui')
nim_container.success('NIM: Tidak Diketahui')

# Create a table to display information
info_table = st.sidebar.table([[f"Nama: {nama_container.info}", f"NIM: {nim_container.success}"]])

st.title("Aplikasi Pengenalan Wajah")
st.write(WEBCAM_PROMPT)

# Camera Setup
kamera = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
FRAME_WINDOW = st.image([])

# Button to start face detection scan
start_scan_button = st.button("Mulai Scan")

# Initialize variables for detected faces
detected_faces = []

while True:
    # Capture frame from the camera
    berhasil, bingkai = kamera.read()

    if not berhasil:
        st.error("Gagal mengambil bingkai dari kamera")
        st.info("Harap matikan aplikasi lain yang menggunakan kamera dan restart aplikasi")
        st.stop()

    if start_scan_button:
        # Process the frame for face recognition
        gambar, nama, nim = recognize(bingkai, TOLERANCE)
        gambar = cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB)

        # Display the name and NIM of the person
        nama_container.info(f"Nama: {nama}")
        nim_container.success(f"NIM: {nim}")

        # Display the frame with Streamlit
        FRAME_WINDOW.image(gambar, channels="RGB")

        # Update the table with the latest information
        if nama != 'Tidak Diketahui' and nim != 'Tidak Diketahui' and (nama, nim) not in detected_faces:
            detected_faces.append((nama, nim))
            info_table.table(detected_faces)

# Release the camera when the app is closed
kamera.release()
