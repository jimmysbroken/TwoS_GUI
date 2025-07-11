import cv2
import mediapipe as mp
import time
import threading
from deteccionGestos import identify_gesture

# Variable global para compartir el frame actual
current_frame = None
running = False

def start_camera():
    global current_frame, running
    running = True
    
    # Inicializa MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils
    
    # Inicializa la cámara
    cap = cv2.VideoCapture(0)
    
    while running:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        
        # Actualizar variable global
        current_frame = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
    
        if results.multi_hand_landmarks:
            for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
                lateralidad = hand_info.classification[0].label
                confidence = hand_info.classification[0].score
                gesture = identify_gesture(hand_landmarks.landmark, lateralidad)
                
                text = f'{lateralidad} ({confidence:.2f})'
                cv2.putText(frame, text, (frame.shape[1] - 200, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
                if gesture is not None:
                    cv2.putText(frame, f'Gesto: {gesture}', (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        time.sleep(0.03)
    
    cap.release()

def stop_camera():
    global running
    running = False