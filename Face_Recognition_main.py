import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import cv2
from utils import recognize  # Pastikan file utils.py sudah ada di direktori yang benar

# Set page configuration
st.set_page_config(layout="wide")

# Sidebar settings
st.sidebar.title("Pengaturan")

# Slider to adjust tolerance
TOLERANCE = st.sidebar.slider("Toleransi", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Toleransi adalah ambang batas untuk pengenalan wajah. Semakin rendah toleransinya, semakin ketat pengenalan wajahnya. Semakin tinggi toleransinya, semakin longgar pengenalan wajahnya.")

# Information Section in sidebar
st.sidebar.title("Informasi Mahasiswa")
nama_container = st.sidebar.empty()
nim_container = st.sidebar.empty()
nama_container.info('Nama: Tidak Diketahui')
nim_container.success('NIM: Tidak Diketahui')

# Create a table to display information
info_table = st.sidebar.table([[f"Nama: {nama_container.info}", f"NIM: {nim_container.success}"]])

# Main app title
st.title("Aplikasi Pengenalan Wajah")

# Initialize variables for detected faces
detected_faces = []

class VideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        super().__init__()

    def recv(self, frame):
        # Process the frame for face recognition
        gambar, nama, nim = recognize(frame, TOLERANCE)
        gambar = cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB)

        # Display the name and NIM of the person
        nama_container.info(f"Nama: {nama}")
        nim_container.success(f"NIM: {nim}")

        # Display the frame with Streamlit
        st.image(gambar, channels="RGB")

        # Update the table with the latest information
        if nama != 'Tidak Diketahui' and nim != 'Tidak Diketahui' and (nama, nim) not in detected_faces:
            detected_faces.append((nama, nim))
            info_table.table(detected_faces)

# Use WebRTC to capture video from the user's camera
webrtc_ctx = webrtc_streamer(
    key="example",
    video_processor_factory=VideoProcessor,
    mode=WebRtcMode.SENDRECV,
)

# Jalankan aplikasi Streamlit
if webrtc_ctx.state.playing:
    st.write("Streaming sedang berjalan...")
