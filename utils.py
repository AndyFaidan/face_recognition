import face_recognition as frg
import pickle as pkl
import os
import cv2
import numpy as np
import yaml
from collections import defaultdict

information = defaultdict(dict)
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
DATASET_DIR = cfg['PATH']['DATASET_DIR']
PKL_PATH = cfg['PATH']['PKL_PATH']

def get_database():
    try:
        with open(PKL_PATH, 'rb') as f:
            database = pkl.load(f)
    except FileNotFoundError:
        # Buat database kosong jika file tidak ditemukan
        database = defaultdict(dict)
        with open(PKL_PATH, 'wb') as f:
            pkl.dump(database, f)
    return database

def recognize(image, TOLERANCE): 
    database = get_database()
    known_encoding = [database[idx]['encoding'] for idx in database.keys()] 
    name = 'Unknown'
    nim = 'Unknown'
    face_locations = frg.face_locations(image)
    face_encodings = frg.face_encodings(image, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = frg.compare_faces(known_encoding, face_encoding, tolerance=TOLERANCE)
        distance = frg.face_distance(known_encoding, face_encoding)
        name = 'Unknown'
        nim = 'Unknown'
        if True in matches:
            match_index = matches.index(True)
            name = database[match_index]['name']
            nim = database[match_index]['nim']
            distance = round(distance[match_index], 2)
            cv2.putText(image, str(distance), (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
    return image, name, nim

def isFaceExists(image): 
    face_location = frg.face_locations(image)
    if len(face_location) == 0:
        return False
    return True

def submitNew(name, nim, image, old_idx=None):
    database = get_database()
    # Read image 
    if type(image) != np.ndarray:
        image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)

    isFaceInPic = isFaceExists(image)
    if not isFaceInPic:
        return -1
    # Encode image
    encoding = frg.face_encodings(image)[0]
    # Append to database
    # Check if nim already exists
    existing_nim = [database[idx]['nim'] for idx in database.keys()]
    # Update mode 
    if old_idx is not None: 
        new_idx = old_idx
    # Add mode
    else: 
        if nim in existing_nim:
            return 0
        new_idx = len(database)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    database[new_idx] = {
        'image': image,
        'nim': nim, 
        'name': name,
        'encoding': encoding
    }
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    return True

def get_info_from_nim(nim): 
    database = get_database() 
    for idx, person in database.items(): 
        if person['nim'] == nim: 
            name = person['name']
            image = person['image']
            return name, image, idx       
    return None, None, None

def deleteOne(nim):
    database = get_database()
    nim = str(nim)
    for key, person in database.items():
        if person['nim'] == nim:
            del database[key]
            break
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    return True

def build_dataset():
    # Pastikan direktori 'dataset' sudah ada
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    counter = 0
    for image in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR, image)
        image_name = image.split('.')[0]
        parsed_name = image_name.split('_')
        person_nim = parsed_name[0]
        person_name = ' '.join(parsed_name[1:])
        if not image_path.endswith('.jpg'):
            continue
        image = frg.load_image_file(image_path)
        information[counter]['image'] = image 
        information[counter]['nim'] = person_nim
        information[counter]['name'] = person_name
        information[counter]['encoding'] = frg.face_encodings(image)[0]
        counter += 1

    with open(os.path.join(DATASET_DIR, 'database.pkl'), 'wb') as f:
        pkl.dump(information, f)

if __name__ == "__main__": 
    build_dataset()
    deleteOne(1)
