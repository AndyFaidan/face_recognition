import streamlit as st
import cv2
import face_recognition as frg
import yaml
import requests
from io import BytesIO
import sounddevice as sd
import numpy as np

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

# Load audio files dynamically from GitHub repository
repo_url = "https://raw.githubusercontent.com/AndyFaidan/face_recognition/Face_Recognition_main.py/"
student_detected_audio_url = repo_url + "audio/StudentIsDetected.mp3"
student_not_detected_audio_url = repo_url + "audio/StudentIsNotDetected.mp3"

# Download audio files
student_detected_audio_content = requests.get(student_detected_audio_url).content
student_not_detected_audio_content = requests.get(student_not_detected_audio_url).content

# Convert audio content to numpy array
student_detected_audio_np = np.frombuffer(student_detected_audio_content, dtype=np.int16)
student_not_detected_audio_np = np.frombuffer(student_not_detected_audio_content, dtype=np.int16)

st.title("Aplikasi Pengenalan Wajah")
st.write(WEBCAM_PROMPT)

# Camera Setup
kamera = cv2.VideoCapture(0)
kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
FRAME_WINDOW = st.image([])

# Button to start face detection scan
start_scan_button = st.button("Mulai Scan")

# Initialize variables for detected faces
detected_faces = []

def play_audio(audio_np):
    sd.play(audio_np, samplerate=44100, blocking=True)

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

            # Play audio when a student is detected
            play_audio(student_detected_audio_np)
        else:
            # Play 'StudentIsNotDetected.mp3' when a face is not recognized
            play_audio(student_not_detected_audio_np)

# Release the camera when the app is closed
kamera.release()
