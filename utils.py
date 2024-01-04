import face_recognition as frg
import pickle as pkl
import os
import cv2
import numpy as np
import yaml
from collections import defaultdict

# Menggunakan DefaultDict untuk database
database = defaultdict(dict)

# Mengambil path dari file konfigurasi langsung
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
PKL_PATH = cfg['PATH']['PKL_PATH']
DATASET_DIR = cfg['PATH']['DATASET_DIR']  # Menambahkan definisi DATASET_DIR dari konfigurasi

def get_database():
    try:
        with open(PKL_PATH, 'rb') as f:
            database = pkl.load(f)
        return database
    except FileNotFoundError:
        return {}

def recognize(image, TOLERANCE):
    database = get_database()
    known_encoding = [database[nim]['encoding'] for nim in database.keys()]
    name, nim = 'Tidak Dikenal', 'Tidak Dikenal'

    face_locations = frg.face_locations(image)
    face_encodings = frg.face_encodings(image, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = frg.compare_faces(known_encoding, face_encoding, tolerance=TOLERANCE)
        distances = frg.face_distance(known_encoding, face_encoding)

        if True in matches:
            match_index = matches.index(True)
            name, nim = database[match_index]['name'], database[match_index]['nim']
            distance = round(distances[match_index], 2)
            cv2.putText(image, str(distance), (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    return image, name, nim

def is_face_exists(image):
    face_location = frg.face_locations(image)
    return len(face_location) != 0

def submit_new(name, nim, image, old_idx=None):
    database = get_database()

    # Baca gambar
    if isinstance(image, np.ndarray):
        image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)

    is_face_in_pic = is_face_exists(image)

    if not is_face_in_pic:
        return -1

    # Encode gambar
    encoding = frg.face_encodings(image)[0]

    # Tambahkan ke database
    # Periksa apakah nim sudah ada
    existing_nim = [database[n]['nim'] for n in database.keys()]

    # Mode pembaruan
    if old_idx is not None:
        new_idx = old_idx
    # Mode penambahan
    else:
        if nim in existing_nim:
            return 0
        new_idx = len(database)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    database[new_idx] = {'image': image, 'nim': nim, 'name': name, 'encoding': encoding}

    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)

    return True

def get_info_from_nim(nim):
    database = get_database()
    for idx, person in database.items():
        if person['nim'] == nim:
            return person['name'], person['image'], idx
    return None, None, None

def delete_one(nim):
    database = get_database()
    nim = str(nim)

    for key, person in list(database.items()):  # Menambahkan fungsi list() agar iterasi tidak terpengaruh saat menghapus item
        if person['nim'] == nim:
            del database[key]
            break

    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)

    return True

def build_dataset():
    for image in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR, image)
        image_name = image.split('.')[0]
        parsed_name = image_name.split('_')
        person_nim = parsed_name[0]
        person_name = ' '.join(parsed_name[1:])

        if not image_path.endswith('.jpg'):
            continue

        image = frg.load_image_file(image_path)
        database[len(database)] = {'image': image, 'nim': person_nim, 'name': person_name, 'encoding': frg.face_encodings(image)[0]}

    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)

if __name__ == "__main__":
    # Gunakan untuk menguji fungsionalitas utils (bila dijalankan sebagai skrip langsung)
    pass
