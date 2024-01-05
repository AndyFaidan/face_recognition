import streamlit as st 
import pickle 
import yaml 
import pandas as pd 

# Mengambil konfigurasi dari file YAML
cfg = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
PKL_PATH = cfg['PATH']["PKL_PATH"]

# Mengatur tata letak halaman Streamlit
st.set_page_config(layout="wide")

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
