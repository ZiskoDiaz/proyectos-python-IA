import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, StringVar
from yt_dlp import YoutubeDL

# Variable global que permite manejar el control de la descarga.
stop_download = threading.Event()

def descargar():
    global stop_download
    stop_download.clear()  # Limpia el evento de la detención de nuestra descarga.

    enlace = entrada_url.get()
    tipo_descarga = opcion_tipo.get()

    if not enlace.strip():
        #si la URL es inválida, dará este mensaje de error.
        messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
        return

    # Configuración inicial del estado de la descarga (hasta que inicie)
    estado_descarga.set("Preparando descarga...")
    
    # Opciones de yt-dlp
    opciones = {
        "quiet": True,  # Acá evitamos que la información se muestre por la terminal.
        "no_warnings": True,  # Ocultamos las advertencias.
        "progress_hooks": [actualizar_progreso],  # Manejamos el estado del progreso de la desacarga.
        "outtmpl": "%(title)s.%(ext)s"  # Preformateamos el nombre del archivo.
    }

    # Configura el formato según el tipo de descarga según elija el usuario.
    if tipo_descarga == "Video":
        opciones["format"] = "bestvideo+bestaudio/best"
    else:  # Audio
        opciones.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })

    # Función para descargar
    def proceso_descarga():
        try:
            with YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(enlace, download=True)
                estado_descarga.set(f"Descarga completada: {info['title']}")
        except Exception as e:
            if stop_download.is_set():
                estado_descarga.set("Descarga cancelada.")
            else:
                estado_descarga.set(f"Error: {e}")

    # Crear y empezar la descarga
    hilo = threading.Thread(target=proceso_descarga, daemon=True)
    hilo.start()

def actualizar_progreso(d):
    #Callback para actualizar el estado de la descarga.
    if stop_download.is_set():
        raise Exception("Descarga abortada por el usuario.")
    if d["status"] == "downloading":
        estado_descarga.set(f"Descargando: {d['_percent_str']} - {d['_speed_str']}")

def cancelar_descarga():
    # Función para cancelar la descarga.
    global stop_download
    stop_download.set()
    estado_descarga.set("Cancelando descarga...")

# Crear la ventana principal
ventana = ttk.Window(themename="flatly")
ventana.title("YouTube Downloader")
ventana.geometry("500x250")
ventana.resizable(False, False)

# Etiqueta para URL
etiqueta_url = ttk.Label(ventana, text="Enlace de YouTube:", font=("Helvetica", 12))
etiqueta_url.pack(pady=5)

# Campo de entrada para URL
entrada_url = ttk.Entry(ventana, width=50)
entrada_url.pack(pady=5)

# Opción de tipo de descarga
opcion_tipo = ttk.StringVar(value="Video")
frame_tipo = ttk.Frame(ventana)
frame_tipo.pack(pady=10)
radio_video = ttk.Radiobutton(frame_tipo, text="Video", variable=opcion_tipo, value="Video", bootstyle="info")
radio_audio = ttk.Radiobutton(frame_tipo, text="Audio", variable=opcion_tipo, value="Audio", bootstyle="success")
radio_video.grid(row=0, column=0, padx=10)
radio_audio.grid(row=0, column=1, padx=10)

# Etiqueta de estado
estado_descarga = StringVar(value="Esperando URL...")
etiqueta_estado = ttk.Label(ventana, textvariable=estado_descarga, font=("Helvetica", 10), bootstyle="secondary")
etiqueta_estado.pack(pady=10)

# Botones
boton_descargar = ttk.Button(ventana, text="Descargar", command=descargar, bootstyle="primary")
boton_descargar.pack(side="left", padx=20, pady=20)
boton_cancelar = ttk.Button(ventana, text="Cancelar", command=cancelar_descarga, bootstyle="danger")
boton_cancelar.pack(side="right", padx=20, pady=20)

# Iniciar la aplicación
ventana.mainloop()