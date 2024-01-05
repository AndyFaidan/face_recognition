import streamlit as st
import cv2
import face_recognition as frg
import yaml 
import pickle 
import numpy as np
from streamlit_option_menu import option_menu
from pydub import AudioSegment
from pydub.playback import play
from utils import recognize, build_dataset, get_database
from utils import submit_new, get_info_from_nim, delete_one
from pydub import AudioSegment

# Tentukan jalur ke ffprobe jika belum ada dalam PATH sistem
AudioSegment.converter = "/opt/homebrew/bin/ffprobe"

# Fungsi untuk memutar suara
def play_audio(file_path):
    try:
        sound = AudioSegment.from_file(file_path)
        play(sound)
    except Exception as e:
        print(f"Error playing audio: {e}")



# Fungsi untuk menampilkan hasil gambar
def display_image_results(image, name, nim):
    st.image(image, caption="Foto yang Diambil")
    name_container.info(f"Nama: {name}")
    nim_container.success(f"NIM: {nim}")

# Path: code\app.py
st.set_page_config(layout="wide")

# Konfigurasi
cfg = yaml.safe_load(open('config.yaml','r'))
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Pengaturan")

#opsi menu
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Gambar", "WebCam", "Update", "Database", ],
        icons=["journal-code", "journal-check","graph-up", "pin-map", "activity"],
        menu_icon="cast",
        default_index=0,
    )

# Tambahkan slider untuk menyesuaikan toleransi
TOLERANCE = st.sidebar.slider("Toleransi", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Toleransi adalah ambang batas untuk pengenalan wajah. Semakin rendah toleransinya, semakin ketat pengenalan wajahnya. Semakin tinggi toleransinya, semakin longgar pengenalan wajahnya.")

# Bagian Informasi
st.sidebar.title("Informasi Mahasiswa")
name_container = st.sidebar.empty()
nim_container = st.sidebar.empty()
name_container.info('Nama: Tidak Dikenal')
nim_container.success('NIM: Tidak Dikenal')

if selected == "Gambar":
    st.title("Aplikasi Pengenalan Wajah")
    st.write(PICTURE_PROMPT)
    uploaded_images = st.file_uploader("Unggah", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

    if len(uploaded_images) != 0:
        # Baca gambar yang diunggah dengan face_recognition
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, nim = recognize(image, TOLERANCE)
            display_image_results(image, name, nim)

            # Memainkan suara tergantung pada apakah wajah terdeteksi atau tidak
            if name != 'Tidak Dikenal':
                play_audio('audio/StudentIsDetected.mp3')
            else:
                play_audio('audio/StudentIsNotDetected.mp3')
                
if selected == "WebCam":
    st.title("Aplikasi Pengenalan Wajah")
    st.write(WEBCAM_PROMPT)

    # Pengaturan Kamera
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_WINDOW = st.image([])

    # Tambahkan tombol untuk memulai pengambilan frame
    start_button = st.button("Mulai Pengambilan Frame")

    # Tambahkan kondisi untuk memproses frame hanya jika tombol ditekan
    if start_button:
        ret, frame = cam.read()
        if not ret:
            st.error("Gagal mengambil frame dari kamera")
            st.info("Harap matikan aplikasi lain yang menggunakan kamera dan restart aplikasi")
        else:
            image, name, nim = recognize(frame, TOLERANCE)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Tampilkan nama dan NIM orang
            name_container.info(f"Nama: {name}")
            nim_container.success(f"NIM: {nim}")
            FRAME_WINDOW.image(image)

            # Memainkan suara tergantung pada apakah wajah terdeteksi atau tidak
            if name != 'Tidak Dikenal':
                play_audio('StudentIsDetected.mp3')
            else:
                play_audio('StudentIsNotDetected.mp3')

    # Bebaskan sumber daya kamera saat aplikasi berakhir
    cam.release()


