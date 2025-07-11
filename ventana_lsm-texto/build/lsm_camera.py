import os
# Silenciar logs de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import logging
logging.getLogger('absl').setLevel(logging.ERROR)
from absl import logging as absl_logging
absl_logging.set_verbosity(absl_logging.ERROR)

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf

import time
import threading
from PIL import Image, ImageDraw, ImageFont

# —————  CONFIG  —————
FRAMES_LSTM = 30
COOLDOWN_SEC = 2.0

# Variables globales
current_frame = None
running = False
modelo = None
clases = None

current_word = None

def initialize_model():
    """Inicializa el modelo y las clases"""
    global modelo, clases
    modelo = tf.keras.models.load_model(r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\ventana_lsm-texto\build\modelo_manos_rostro_aumentado.h5")
    clases = np.load(r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\ventana_lsm-texto\build\clases_manos_rostro_aumentado.npy", allow_pickle=True)

def draw_text_unicode(img, text, pos, font_size=40, color=(0,255,0)):
    """Dibuja texto con soporte Unicode usando PIL"""
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    rgb_color = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=rgb_color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def start_camera():
    """Inicia la detección LSM en tiempo real"""
    global current_frame, running
    running = True
    
    # Inicializar modelo si no está cargado
    if modelo is None:
        initialize_model()
    
    # —————  MEDIAPIPE  —————
    mp_hands = mp.solutions.hands
    mp_face = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    hands = mp_hands.Hands(max_num_hands=2,
                           min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)

    face_mesh = mp_face.FaceMesh(static_image_mode=False,
                                 max_num_faces=1,
                                 refine_landmarks=True,
                                 min_detection_confidence=0.7,
                                 min_tracking_confidence=0.7)

    # Conexiones faciales
    FACE_CONNECTIONS = [
        mp_face.FACEMESH_CONTOURS,
        mp_face.FACEMESH_LEFT_EYE,
        mp_face.FACEMESH_RIGHT_EYE,
        mp_face.FACEMESH_LEFT_EYEBROW,
        mp_face.FACEMESH_RIGHT_EYEBROW,
        mp_face.FACEMESH_FACE_OVAL,
        mp_face.FACEMESH_NOSE,
        mp_face.FACEMESH_LIPS,
    ]

    cap = cv2.VideoCapture(0)
    buffer = []
    last_time = time.time() - COOLDOWN_SEC

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        current_frame = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar manos y rostro
        res_h = hands.process(rgb)
        res_f = face_mesh.process(rgb)

        # Inicializar vectores
        m1 = [0.0]*42; m2 = [0.0]*42; r = [0.0]*36

        # Extraer manos
        if res_h.multi_hand_landmarks:
            for i, hand in enumerate(res_h.multi_hand_landmarks):
                pts = [lm.x for lm in hand.landmark] + [lm.y for lm in hand.landmark]
                if len(pts)==42:
                    (m1 if i==0 else m2)[:] = pts
                

        # Extraer rostro
        if res_f.multi_face_landmarks:
            face = res_f.multi_face_landmarks[0]
            idxs = [33,263,61,291,199,4,0,17,267,37,164,393,78,308,13,14,312,82]
            coords = []
            for idx in idxs:
                lm = face.landmark[idx]
                coords += [lm.x, lm.y]
            if len(coords)==36:
                r[:] = coords
            

        # Agregar al buffer solo con manos
        if any(m1) or any(m2):
            buffer.append(m1 + m2 + r)
            if len(buffer)>FRAMES_LSTM:
                buffer.pop(0)

        # Predicción
        now = time.time()
        if len(buffer)==FRAMES_LSTM and (now - last_time)>=COOLDOWN_SEC:
            inp = np.array(buffer).reshape(1, FRAMES_LSTM, 120).astype(np.float32)
            pred = modelo.predict(inp, verbose=0)
            palabra = clases[np.argmax(pred)]
            last_time = now
            buffer.clear()
            
            # Actualizar palabra global
            global current_word
            current_word = palabra
            print(palabra)
        current_frame = frame
        time.sleep(0.01)

    cap.release()

def stop_camera():
    """Detiene la cámara"""
    global running
    running = False

def get_current_frame():
    """Retorna el frame actual"""
    return current_frame