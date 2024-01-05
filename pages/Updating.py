import streamlit as st 
import cv2
import yaml 
import pickle 
from utils import submit_new, get_info_from_nim, delete_one
import numpy as np

st.set_page_config(layout="wide")
st.title("Aplikasi Pengenalan Wajah")
st.write("Aplikasi ini digunakan untuk menambahkan wajah baru ke dataset")

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
