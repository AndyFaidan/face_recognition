import streamlit as st 
import cv2
import yaml 
import pickle 
from utils import submitNew, get_info_from_nim, deleteOne
import numpy as np

st.set_page_config(layout="wide")
st.title("Face Recognition App")
st.write("This app is used to add new faces to the dataset")

menu = ["Adding", "Deleting", "Adjusting"]
choice = st.sidebar.selectbox("Options", menu)
if choice == "Adding":
    name = st.text_input("Name", placeholder='Enter name')
    nim = st.text_input("NIM", placeholder='Enter NIM')
    upload = st.radio("Upload image or use webcam", ("Upload", "Webcam"))
    if upload == "Upload":
        uploaded_image = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])
        if uploaded_image is not None:
            st.image(uploaded_image)
            submit_btn = st.button("Submit", key="submit_btn")
            if submit_btn:
                if name == "" or nim == "":
                    st.error("Please enter name and NIM")
                else:
                    ret = submitNew(name, nim, uploaded_image)
                    if ret == 1:
                        st.success("Student Added")
                    elif ret == 0:
                        st.error("Student NIM already exists")
                    elif ret == -1:
                        st.error("There is no face in the picture")
    elif upload == "Webcam":
        img_file_buffer = st.camera_input("Take a picture")
        submit_btn = st.button("Submit", key="submit_btn")
        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            if submit_btn:
                if name == "" or nim == "":
                    st.error("Please enter name and NIM")
                else:
                    ret = submitNew(name, nim, cv2_img)
                    if ret == 1:
                        st.success("Student Added")
                    elif ret == 0:
                        st.error("Student NIM already exists")
                    elif ret == -1:
                        st.error("There is no face in the picture")
elif choice == "Deleting":
    def del_btn_callback(nim):
        deleteOne(nim)
        st.success("Student deleted")

    nim = st.text_input("NIM", placeholder='Enter NIM')
    submit_btn = st.button("Submit", key="submit_btn")
    if submit_btn:
        name, image, _ = get_info_from_nim(nim)
        if name is None and image is None:
            st.error("Student NIM does not exist")
        else:
            st.success(f"Name of student with NIM {nim} is: {name}")
            st.warning("Please check the image below to make sure you are deleting the right student")
            st.image(image)
            del_btn = st.button("Delete", key="del_btn", on_click=del_btn_callback, args=(nim,))
elif choice == "Adjusting":
    def form_callback(old_name, old_nim, old_image, old_idx):
        new_name = st.session_state['new_name']
        new_nim = st.session_state['new_nim']
        new_image = st.session_state['new_image']

        name = old_name
        nim = old_nim
        image = old_image

        if new_image is not None:
            image = cv2.imdecode(np.frombuffer(new_image.read(), np.uint8), cv2.IMREAD_COLOR)

        if new_name != old_name:
            name = new_name

        if new_nim != old_nim:
            nim = new_nim

        ret = submitNew(name, nim, image, old_idx=old_idx)
        if ret == 1:
            st.success("Student Added")
        elif ret == 0:
            st.error("Student NIM already exists")
        elif ret == -1:
            st.error("There is no face in the picture")

    nim = st.text_input("NIM", placeholder='Enter NIM')
    submit_btn = st.button("Submit", key="submit_btn")
    if submit_btn:
        old_name, old_image, old_idx = get_info_from_nim(nim)
        if old_name is None and old_image is None:
            st.error("Student NIM does not exist")
        else:
            with st.form(key='my_form'):
                st.title("Adjusting student info")
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Name", key='new_name', value=old_name, placeholder='Enter new name')
                new_nim = col1.text_input("NIM", key='new_nim', value=nim, placeholder='Enter new NIM')
                new_image = col1.file_uploader("Upload new image", key='new_image', type=['jpg', 'png', 'jpeg'])
                col2.image(old_image, caption='Current image', width=400)
                st.form_submit_button(label='Submit', on_click=form_callback, args=(old_name, nim, old_image, old_idx))

