import streamlit as st 
import pickle 
import yaml 
import pandas as pd 

cfg = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
PKL_PATH = cfg['PATH']["PKL_PATH"]
st.set_page_config(layout="wide")

# Load database 
with open(PKL_PATH, 'rb') as file:
    database = pickle.load(file)

Index, Nim, Name, Image = st.columns([0.5, 0.5, 3, 3])  # Ganti 'Id' menjadi 'Nim'

for idx, person in database.items():
    with Index:
        st.write(idx)
    with Nim:  # Ganti 'Id' menjadi 'Nim'
        st.write(person['nim'])  # Ganti 'id' menjadi 'nim'
    with Name:     
        st.write(person['name'])
    with Image:     
        st.image(person['image'], width=200)
