from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, Label
from PIL import Image, ImageTk
import pyttsx3
import threading
import cv2
import time
from lsm_camera import current_frame, start_camera, stop_camera, current_word

# Configuración de paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\ventana_lsm-texto\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Configuración de la ventana principal
window = Tk()
window.geometry("1080x640")
window.configure(bg="#E8E8E8")

canvas = Canvas(
    window,
    bg = "#E8E8E8",
    height = 640,
    width = 1080,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    540.0,
    320.0,
    image=image_image_1
)

# Label para mostrar el video
video_image = PhotoImage(file=relative_to_assets("fondoo.png"))
video_label = Label(window, image=video_image)
video_label.place(x=540, y=109, width=470, height=264)

# Variables para el texto y voz
current_text_id = None
last_spoken_word = None
is_speaking = False

# Inicializar pyttsx3 una sola vez con driver específico
try:
    engine = pyttsx3.init('sapi5')  # Windows SAPI5 para mejor rendimiento
except:
    engine = pyttsx3.init()  # Fallback al driver por defecto

engine.setProperty('rate', 160)  # Velocidad ligeramente más rápida
engine.setProperty('volume', 1.0)  # Volumen máximo

# Configurar voz en español si está disponible
voices = engine.getProperty('voices')
for voice in voices:
    if 'spanish' in voice.name.lower() or 'es' in voice.id.lower() or 'helena' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Pre-calentar el motor
engine.say("")
engine.runAndWait()

def hablar_palabra(palabra):
    global is_speaking
    def speak():
        global is_speaking
        try:
            is_speaking = True
            # Pequeña pausa para estabilizar
            time.sleep(0.05)
            
            # Limpiar cola de voz anterior
            engine.stop()
            
            # Agregar palabra con pausa al final
            engine.say(f"{palabra}.")
            engine.runAndWait()
            
            # Pausa adicional para evitar cortes
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error en hablar_palabra: {e}")
        finally:
            is_speaking = False
    
    threading.Thread(target=speak, daemon=True).start()

def show_video_text(text):
    global current_text_id, last_spoken_word
    if current_text_id:
        canvas.delete(current_text_id)
    
    x_center = 614.0 + (307.0 / 2)
    y_position = 430.0
    
    current_text_id = canvas.create_text(
        x_center,
        y_position,
        anchor="center",
        text=text,
        fill="#FFFFFF",
        font=("League Spartan", 60, 'bold')
    )
    
    if text != last_spoken_word and not is_speaking:
        last_spoken_word = text
        hablar_palabra(text)

def update_video():
    import lsm_camera
    if lsm_camera.current_frame is not None:
        try:
            # Convertir BGR a RGB
            frame_rgb = cv2.cvtColor(lsm_camera.current_frame, cv2.COLOR_BGR2RGB)
            # Redimensionar
            img = Image.fromarray(frame_rgb)
            img = img.resize((470, 264), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            
            video_label.imgtk = imgtk
            video_label.config(image=imgtk)
        except Exception as e:
            print(f"Error actualizando video: {e}")
    
    # Actualizar texto si hay nueva palabra
    if lsm_camera.current_word:
        show_video_text(lsm_camera.current_word)
    
    window.after(30, update_video)

def start_video():
    threading.Thread(target=start_camera, daemon=True).start()
    # Esperar un poco antes de iniciar la actualización
    window.after(300, update_video)

# Configurar botones
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    window,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=start_video,
    relief="flat",
    cursor="hand2",
    activebackground="#454545"
)
button_1.place(x=42.0, y=293.0, width=441.0, height=134.0)

# Botón para detener (opcional)
button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    window,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=stop_camera,
    relief="flat",
    cursor="hand2",
    activebackground="#3A3A39"
)
button_2.place(x=40.0, y=465.0, width=311.0, height=121.0)

window.resizable(False, False)
window.mainloop()