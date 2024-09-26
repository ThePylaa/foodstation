import tkinter as tk
from tkinter import font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import *
from ui.welcomePage import WelcomePage
from ui.wifiSetup import WifiSetup
from ui.wifiSetupErrorPage import WifiSetupErrorPage
from ui.wifiSetupSuccess import WifiSetupSuccess
from ui.registerStation import RegisterStation
from ui.registerStationErrorPage import RegisterStationErrorPage
from ui.registerStationSuccess import RegisterStationSuccess
from ui.addAnimal import AddAnimal
from ui.overview import Overview

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Station Setup Application")
        
        # Setze den Vollbildmodus sofort
        self.attributes('-fullscreen', True)
        
        # Definiere die Hauptschriftart mit Fallback
        self.main_font = tkfont.Font(family='Roboto, Helvetica, Arial', size=14, weight="normal")
        
        # Initialisiere den Stil mit ttkbootstrap
        self.style = ttk.Style(theme="darkly")
        self.style.configure("TButton", font=self.main_font, padding=5)
        self.style.configure("TEntry", font=self.main_font, padding=5)
        self.style.configure("TLabel", font=self.main_font, padding=5)

        # Erstelle den Container für die Frames
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")  
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1)  
        self.container.grid_rowconfigure(0, weight=1)  
        self.container.grid_columnconfigure(0, weight=1)  

        # Dictionary zur Speicherung der Frames
        self.frames = {}
        self.create_frames()

        # Zeige das Start-Frame an
        self.show_frame("Overview")

    def create_frames(self):
        """Erstellt und speichert alle Frames in der Anwendung."""
        frame_classes = (
            WelcomePage, WifiSetup, WifiSetupErrorPage, WifiSetupSuccess, RegisterStation, 
            RegisterStationErrorPage, RegisterStationSuccess, AddAnimal, Overview
        )
        for FrameClass in frame_classes:
            try:
                frame = FrameClass(parent=self.container, controller=self)
                self.frames[FrameClass.__name__] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                print(f"Error creating frame {FrameClass.__name__}: {str(e)}")
                raise  # Optional: Entferne das `raise`, wenn du möchtest, dass die App weiterläuft

    def show_frame(self, page_name):
        """Hebt das angegebene Frame hervor, sodass es sichtbar wird."""
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
        else:
            print(f"Frame {page_name} not found")


if __name__ == "__main__":
    try:
        app = MainApp()
        app.mainloop()
    except Exception as e:
        print(f"An error occurred while running the application: {str(e)}")
