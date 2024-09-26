#!/usr/bin/env python3

import tkinter as tk
from tkinter import StringVar
import time
import threading
from arduinoCommunication import recievePayload, dispensePortion
import os 

# Warte auf das Vorhandensein der DISPLAY-Umgebungsvariable
while 'DISPLAY' not in os.environ:
    print("Warten auf Display...")
    time.sleep(1)

# Funktion, die den Payload aktualisiert

def update_label():
    while True:
        payload = recievePayload()
        payload_var.set(payload)
        time.sleep(1)

# Erstelle das Hauptfenster
root = tk.Tk()
root.title("Payload Anzeige")

# Variable für den Payload
payload_var = StringVar()
payload_var.set("Warten auf Payload...")

# Erstelle und platziere ein Label, das den Payload anzeigt
label = tk.Label(root, textvariable=payload_var, font=("Helvetica", 16))
label.pack(pady=20, padx=20)

# Startet den Thread, der die Payload aktualisiert
thread = threading.Thread(target=update_label, daemon=True)
thread.start()

# Hauptschleife starten
root.mainloop()
