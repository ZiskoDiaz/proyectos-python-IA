import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import pygame
from PIL import Image, ImageTk

# Constantes de configuración
BG_COLOR = "#f0f0f0"
FG_COLOR = "#555"
ICON_SIZE = (50, 50)
# Se espera que la carpeta "icons" esté en el mismo directorio que este script
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música")
        self.root.geometry("500x450")
        self.root.configure(bg=BG_COLOR)

        # Inicializamos pygame mixer
        try:
            pygame.mixer.init()
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar el mixer: {e}")
            self.root.destroy()
            return

        # Variables de estado
        self.current_song = None
        self.is_paused = False

        # Configuración de arrastrar y soltar
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

        # Configuración de la interfaz
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz gráfica principal."""
        # Título
        title_label = tk.Label(
            self.root,
            text="🎵 Reproductor de Música 🎵",
            font=("Arial", 18),
            bg=BG_COLOR,
        )
        title_label.pack(pady=10)

        # Etiqueta para mostrar la canción actual
        self.song_label = tk.Label(
            self.root,
            text="Arrastra una canción aquí o usa el botón de cargar",
            font=("Arial", 12),
            wraplength=400,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        self.song_label.pack(pady=10)

        # Botón para cargar canción
        load_button = tk.Button(
            self.root,
            text="Cargar Canción",
            font=("Arial", 12),
            command=self.load_song,
            bg="#4caf50",
            fg="white",
        )
        load_button.pack(pady=5)

        # Control de volumen
        volume_frame = tk.Frame(self.root, bg=BG_COLOR)
        volume_frame.pack(pady=5)
        volume_label = tk.Label(
            volume_frame, text="Volumen:", font=("Arial", 10), bg=BG_COLOR
        )
        volume_label.pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.set_volume,
            bg=BG_COLOR,
        )
        self.volume_slider.set(70)  # Valor predeterminado
        self.volume_slider.pack(side=tk.LEFT, padx=10)

        # Controles de reproducción
        control_frame = tk.Frame(self.root, bg=BG_COLOR)
        control_frame.pack(pady=20)
        self.icons = self.load_icons()

        play_button = tk.Button(
            control_frame,
            image=self.icons["play"],
            command=self.play_song,
            bg=BG_COLOR,
            borderwidth=0,
        )
        play_button.grid(row=0, column=0, padx=10)

        pause_button = tk.Button(
            control_frame,
            image=self.icons["pause"],
            command=self.pause_song,
            bg=BG_COLOR,
            borderwidth=0,
        )
        pause_button.grid(row=0, column=1, padx=10)

        stop_button = tk.Button(
            control_frame,
            image=self.icons["stop"],
            command=self.stop_song,
            bg=BG_COLOR,
            borderwidth=0,
        )
        stop_button.grid(row=0, column=2, padx=10)

    def load_icons(self):
        """Carga y redimensiona los iconos desde la carpeta de iconos."""
        icons = {}
        try:
            icons["play"] = ImageTk.PhotoImage(
                Image.open(os.path.join(ICON_DIR, "play.png")).resize(ICON_SIZE)
            )
            icons["pause"] = ImageTk.PhotoImage(
                Image.open(os.path.join(ICON_DIR, "pause.png")).resize(ICON_SIZE)
            )
            icons["stop"] = ImageTk.PhotoImage(
                Image.open(os.path.join(ICON_DIR, "stop.png")).resize(ICON_SIZE)
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los iconos: {e}")
        return icons

    def on_drop(self, event):
        """Maneja el evento de arrastrar y soltar archivos."""
        file_path = event.data.strip().strip("{}")
        if file_path.lower().endswith(".mp3"):
            self.load_song_from_path(file_path)
        else:
            self.song_label.config(
                text="Formato no soportado. Selecciona un archivo .mp3."
            )

    def load_song_from_path(self, file_path):
        """Carga la canción desde la ruta especificada."""
        self.current_song = file_path
        song_name = os.path.basename(file_path)
        self.song_label.config(text=f"Canción: {song_name}")
        try:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.set_volume(self.volume_slider.get() / 100)
            self.is_paused = False
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la canción: {e}")

    def load_song(self):
        """Carga una canción usando el diálogo de archivos."""
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Audio", "*.mp3")])
        if file_path:
            self.load_song_from_path(file_path)

    def play_song(self):
        """Reproduce la canción cargada."""
        if self.current_song:
            try:
                if self.is_paused:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.play()
                self.is_paused = False
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reproducir la canción: {e}")

    def pause_song(self):
        """Pausa la canción en reproducción."""
        if self.current_song and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop_song(self):
        """Detiene la reproducción de la canción."""
        if self.current_song:
            pygame.mixer.music.stop()
            self.is_paused = False

    def set_volume(self, volume):
        """Ajusta el volumen de reproducción."""
        try:
            vol = int(volume) / 100
            pygame.mixer.music.set_volume(vol)
        except Exception as e:
            print("Error al ajustar el volumen:", e)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MusicPlayer(root)
    root.mainloop()