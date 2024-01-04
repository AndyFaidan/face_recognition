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

# Fungsi untuk memutar suara
def play_audio(file_path):
    sound = AudioSegment.from_file(file_path)
    play(sound)

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
    uploaded_images = st.file_uploader("Unggah", type=['jpg','png','jpeg'], accept_multiple_files=True)
    
    if len(uploaded_images) != 0:
        # Baca gambar yang diunggah dengan face_recognition
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, nim = recognize(image, TOLERANCE) 
            display_image_results(image, name, nim)

            # Memainkan suara tergantung pada apakah wajah terdeteksi atau tidak
            if name != 'Tidak Dikenal':
                play_audio('StudentIsDetected.mp3')
            else:
                play_audio('StudentIsNotDetected.mp3')
                
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

if selected == "Update":
    menu = ["Menambahkan", "Menghapus", "Menyesuaikan"]
    choice = st.sidebar.selectbox("Pilihan", menu)

    if choice == "Menambahkan":
        nama = st.text_input("Nama", placeholder='Masukkan nama')
        nim = st.text_input("NIM", placeholder='Masukkan NIM')
        
        upload = st.radio("Unggah gambar atau gunakan webcam", ("Unggah", "Webcam"))
        
        if upload == "Unggah":
            uploaded_image = st.file_uploader("Unggah", type=['jpg','png','jpeg'])
            
            if uploaded_image is not None:
                st.image(uploaded_image)
                submit_btn = st.button("Kirim", key="submit_btn")
                
                if submit_btn:
                    if nama == "" or nim == "":
                        st.error("Harap masukkan nama dan NIM")
                    else:
                        ret = submit_new(nama, nim, uploaded_image)
                        
                        if ret == 1: 
                            st.success("Mahasiswa Ditambahkan")
                        elif ret == 0: 
                            st.error("NIM Mahasiswa sudah ada")
                        elif ret == -1: 
                            st.error("Tidak ada wajah dalam gambar")
                            
        elif upload == "Webcam":
            img_file_buffer = st.camera_input("Ambil gambar")
            submit_btn = st.button("Kirim", key="submit_btn")
            
            if img_file_buffer is not None:
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                
                if submit_btn: 
                    if nama == "" or nim == "":
                        st.error("Harap masukkan nama dan NIM")
                    else:
                        ret = submit_new(nama, nim, cv2_img)
                        
                        if ret == 1: 
                            st.success("Mahasiswa Ditambahkan")
                        elif ret == 0: 
                            st.error("NIM Mahasiswa sudah ada")
                        elif ret == -1: 
                            st.error("Tidak ada wajah dalam gambar")

    elif choice == "Menghapus":
        def del_btn_callback(nim):
            delete_one(nim)
            st.success("Mahasiswa dihapus")
            
        nim = st.text_input("NIM", placeholder='Masukkan NIM')
        submit_btn = st.button("Kirim", key="submit_btn")
        
        if submit_btn:
            nama, image, _ = get_info_from_nim(nim)
            
            if nama == None and image == None:
                st.error("NIM Mahasiswa tidak ditemukan")
            else:
                st.success(f"Nama Mahasiswa dengan NIM {nim} adalah: {nama}")
                st.warning("Silakan periksa gambar di bawah untuk memastikan Anda menghapus mahasiswa yang benar")
                st.image(image)
                del_btn = st.button("Hapus", key="del_btn", on_click=del_btn_callback, args=(nim,))
                
    elif choice == "Menyesuaikan":
        def form_callback(old_nama, old_nim, old_image, old_idx):
            new_nama = st.session_state['new_nama']
            new_nim = st.session_state['new_nim']
            new_image = st.session_state['new_image']
            
            nama = old_nama
            nim = old_nim
            image = old_image
            
            if new_image is not None:
                image = cv2.imdecode(np.frombuffer(new_image.read(), np.uint8), cv2.IMREAD_COLOR)
                
            if new_nama != old_nama:
                nama = new_nama
                
            if new_nim != old_nim:
                nim = new_nim
            
            ret = submit_new(nama, nim, image, old_idx=old_idx)
            
            if ret == 1: 
                st.success("Mahasiswa Ditambahkan")
            elif ret == 0: 
                st.error("NIM Mahasiswa sudah ada")
            elif ret == -1: 
                st.error("Tidak ada wajah dalam gambar")
                
        nim = st.text_input("NIM", placeholder='Masukkan NIM')
        submit_btn = st.button("Kirim", key="submit_btn")
        
        if submit_btn:
            old_nama, old_image, old_idx = get_info_from_nim(nim)
            
            if old_nama == None and old_image == None:
                st.error("NIM Mahasiswa tidak ditemukan")
            else:
                with st.form(key='my_form'):
                    st.title("Menyesuaikan informasi mahasiswa")
                    col1, col2 = st.columns(2)
                    new_nama = col1.text_input("Nama", key='new_nama', value=old_nama, placeholder='Masukkan nama baru')
                    new_nim  = col1.text_input("NIM", key='new_nim', value=nim, placeholder='Masukkan NIM baru')
                    new_image = col1.file_uploader("Unggah gambar baru", key='new_image', type=['jpg','png','jpeg'])
                    col2.image(old_image, caption='Gambar saat ini', width=400)
                    st.form_submit_button(label='Kirim', on_click=form_callback, args=(old_nama, nim, old_image, old_idx))

elif selected == "Database":
    # Mengambil konfigurasi dari file YAML
    cfg = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    PKL_PATH = cfg['PATH']["PKL_PATH"]

    # Mengatur tata letak halaman Streamlit
    # st.set_page_config(layout="wide")  # Remove or comment out this line

    # Memuat database
    with open(PKL_PATH, 'rb') as file:
        database = pickle.load(file)

    # Membuat kolom-kolom untuk menampilkan informasi
    Indeks, NIM, Nama, Gambar = st.columns([0.5, 0.5, 3, 3])

    # Menampilkan informasi setiap wajah dalam database
    for idx, person in database.items():
        with Indeks:
            st.write(idx)
        with NIM: 
            st.write(person['nim'])
        with Nama:     
            st.write(person['name'])
        with Gambar:     
            st.image(person['image'], width=200)
