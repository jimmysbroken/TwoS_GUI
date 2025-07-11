from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label
from PIL import Image, ImageTk
import cv2
import os
import time
from vosk import Model, KaldiRecognizer
import pyaudio
import json
# Configuración inicial
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\ventana_texto-lsm\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Carpeta donde están los videos (¡cambia esto a tu ruta!)
VIDEOS_FOLDER = r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\vid_tuskpik"

# Variables para controlar la visibilidad de la imagen de fondo
entry_bg_visible = False

# Clase para manejar la reproducción de video
class VideoPlayer:
    def __init__(self, window):
        self.window = window
        self.video = None
        self.is_playing = False
        self.video_queue = []
        self.video_image = PhotoImage(file=relative_to_assets("image_4.png"))
        self.video_label = Label(window, image=self.video_image)
        self.video_label.place(x=592, y=231, width=451, height=253)
        self.current_text_id = None  # Para almacenar el ID del texto actual
        
    def show_video_text(self, text):
        if self.current_text_id:
            canvas.delete(self.current_text_id)
        
        # Calcular posición central
        x_center = 614.0 + (375.0 / 2)  # Centro del área donde quieres el texto
        y_position = 520.0
        
        self.current_text_id = canvas.create_text(
            x_center,  # Posición X centrada
            y_position,  # Posición Y
            anchor="center",  # Esto centrará el texto horizontalmente
            text=text,
            fill="#FFFFFF",
            font=("League Spartan", 40, 'bold'),
              # Ancho máximo para envolver texto
        )
    
    def clear_video_text(self):
        if self.current_text_id:
            canvas.delete(self.current_text_id)
            self.current_text_id = None
            
              
    def play_video(self, video_path):
        if os.path.exists(video_path):
            self.stop_video()
            self.video = cv2.VideoCapture(video_path)
            self.is_playing = True
            
            # Mostrar texto con el nombre del archivo (sin la ruta ni extensión)
            titulo_vid = os.path.splitext(os.path.basename(video_path))[0]
            video_name = titulo_vid[0].upper() + titulo_vid[1:].lower()
            video_name = video_name.replace(".", "?")
            self.show_video_text(video_name.replace("_", " ").title())
            
            self.update_frame()
        else:
            print(f"Error: Archivo no encontrado - {video_path}")
    
    def update_frame(self):
        if self.is_playing and self.video:
            start_time = time.time()
            ret, frame = self.video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (451, 253))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
                
                processing_time = (time.time() - start_time) * 1000
                target_delay = 30
                adjusted_delay = max(1, int(target_delay - processing_time))
                
                self.window.after(adjusted_delay, self.update_frame)
            else:
                self.stop_video()
                if self.video_queue:
                    next_video = self.video_queue.pop(0)
                    self.window.after(500, lambda: self.play_video(next_video))
    
    def stop_video(self):
        self.is_playing = False
        if self.video:
            self.video.release()
        self.video_label.config(image=self.video_image)
        self.clear_video_text()  # Limpiar texto al detener el video
        
def entrada():
    
    encontrado = False
    nombre_video = entry_1.get("1.0", "end-1c").strip().lower()
    nombre_video = nombre_video.replace(",", "")
    
      
    entry_1.delete(1.0, "end")
    buscar_y_rep(nombre_video)

def buscar_y_rep(texto):
    texto = texto.replace("?", ".")
    textoSeparado = texto.split()
    x = 1
    y = 0
    for i in texto:
        if i == " ":
            x += 1
    palRes = x
    antGuion = 0
    posicion = 0
    videos = []
    coincidencia = False
    archivos = os.listdir(VIDEOS_FOLDER)
    palabra = textoSeparado[0]
    encontrado = True
    encontrado_ = False
    
    while True:
        encontrado = False
        
        if palRes == 0:
            break
        for i in archivos:
            
            if (palabra + ".mp4") == i and palRes == 1:
                videos.append(os.path.join(VIDEOS_FOLDER,i))
                encontrado = True
                textoSeparado.pop(0)
                palRes -= 1
                print(palRes)
                break
        if encontrado == False:
            encontrado_ = False
            palabra = palabra + "_"
            textoSeparado.pop(0)
            palRes -= 1
            for i in archivos:
                if encontrado_:
                    break
                while True:
                    if encontrado_:
                        palabra += "_"
                    encontrado = False
                    if palabra == i[0:(len(palabra))] and i[len(palabra)] != ".":
                        palabra = palabra + textoSeparado[0] + "_"
                        textoSeparado.pop(0)
                        palRes -= 1
                    else:
                        if (palabra[0:(len(palabra)-1)] + ".mp4") == i:
                            videos.append(os.path.join(VIDEOS_FOLDER, i))
                            if palRes >= 1:
                                palabra = textoSeparado[0]
                            encontrado_ = True
                        break

            
        if palRes == 0:
            break   
    
    player.video_queue = videos[1:]  # Todos menos el primero   
    player.play_video(videos[0])
    
def rep_vid(titulo_vid, carpeta):
    titulo_arch = f"{titulo_vid.lower()}.mp4"
    ruta_video = os.path.join(carpeta, titulo_arch)
    
    if os.path.exists(ruta_video):
        if os.name == "nt":
            os.startfile(ruta_video)
            return True
    else:
        print(f"No se encontró el video '{titulo_vid}.mp4'")
        return False   


def dictado():
    modelo_path = r"C:\Users\jjhzu\OneDrive\Documentos\simpleGUI\ventana_texto-lsm\vosk-model-small-es-0.42"
    modelo = Model(modelo_path)
    recognizer = KaldiRecognizer(modelo, 16000)
    recognizer.SetWords(True)
    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192
    )
    listening_text = canvas.create_text(
        315.0,  # Posición X
        590.0,  # Posición Y
        text="Escuchando...",
        fill="#FFFFFF",
        font=("League Spartan", 38, 'bold'),
        anchor="center",
        tags="listening_text"
    )
    window.update_idletasks()
    window.update()
    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                resultado = json.loads(recognizer.Result())
                texto = resultado.get('text', '')
                if texto:
                    texto = texto.replace(" signo de pregunta", "?")
                    print(texto)
                    break
    finally:
        canvas.delete(listening_text)
        stream.stop_stream()
        stream.close()
        mic.terminate()
        buscar_y_rep(texto)


# Funciones para mostrar/ocultar elementos (originales)
def mostrar_button_1():
    button_1.place(x=143.0, y=236.0, width=327.0, height=320.0)
    button_2.place_forget()
    entry_1.place_forget()
    global entry_bg_visible
    if entry_bg_visible:
        canvas.itemconfigure(entry_bg_1, state='hidden')
        entry_bg_visible = False
    player.stop_video()  # Detener video si está reproduciéndose

def mostrar_entry_button2():
    entry_1.place(x=73.0, y=231.0, width=453.0, height=275.0)
    button_2.place(x=200.0, y=534.0, width=202.0, height=63.0)
    button_1.place_forget()
    global entry_bg_visible
    canvas.itemconfigure(entry_bg_1, state='normal')
    entry_bg_visible = True

# Configuración de la ventana
window = Tk()
window.geometry("1080x640")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=640,
    width=1080,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(540.0, 320.0, image=image_image_1)



entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    299.5,
    369.5,
    image=entry_image_1,
    state='hidden'
)
entry_1 = Text(
    window,
    bd=0,
    bg="#888888",
    fg="#FFFFFF",
    font=("League Spartan", 28, "bold"),
    highlightthickness=0,
)


button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    window,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=dictado,
    relief="flat",
    activebackground="#4E4E4E",
    cursor="hand2"
)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    window,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=entrada,  
    relief="flat",
    activebackground="#595959",
    cursor="hand2"
)

button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_3 = Button(
    window,
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=mostrar_button_1,
    relief="flat",
    activebackground="#373737",
    cursor="hand2"
)
button_3.place(x=78.0, y=119.0, width=203.0, height=64.0)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    300.0,
    64.0,
    image=image_image_2
)


button_image_4 = PhotoImage(file=relative_to_assets("button_4.png"))
button_4 = Button(
    window,
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=mostrar_entry_button2,
    relief="flat",
    activebackground="#393939",
    cursor="hand2"
)
button_4.place(x=327.0, y=119.0, width=208.0, height=64.0)

image_image_3 = PhotoImage(
    file=relative_to_assets("tuspik.png"))
image_3 = canvas.create_image(
    824.0,
    108.0,
    image=image_image_3
)

# Inicializar el reproductor de video
player = VideoPlayer(window)


button_1.place_forget()
button_2.place_forget()
entry_1.place_forget()

window.resizable(False, False)
window.mainloop()