import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk 
from arduinoCommunication import getRFID
import threading
import time
from VKeyboard import VKeyboard

class AddAnimal(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.animal_rfid = tk.StringVar()
        self.animal_name = tk.StringVar()
        self.animal_type = tk.StringVar(value="Cat")  
        self.searching = False
        self.saved_animals = []  
        self.create_widgets()
        self.VKeyboard = VKeyboard(self)

        self.keyboard_visible = False  

        
        self.bind("<Button-1>", self.on_click)

       
        self.animal_name.trace_add("write", self.on_name_change)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Titel
        title = ttk.Label(self, text="Add an Animal", font=("Helvetica", 24, "bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Anweisungen
        instructions = ttk.Label(self, text="Click 'Search' to scan for an RFID tag",
                                 font=("Helvetica", 14))
        instructions.grid(row=1, column=0, pady=(0, 20))

        # RFID-Anzeige
        self.rfid_display = ttk.Label(self, textvariable=self.animal_rfid,
                                      font=("Helvetica", 18, "bold"))
        self.rfid_display.grid(row=2, column=0, pady=(0, 20))

        # Tier-Info-Frame
        self.animal_info_frame = ttk.Frame(self)
        self.animal_info_frame.grid(row=3, column=0, pady=(0, 20), sticky="nsew")
        self.animal_info_frame.grid_columnconfigure(1, weight=1)

        # Tiername
        ttk.Label(self.animal_info_frame, text="Animal Name:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(10, 0), pady=5)
        self.name_entry = tk.Entry(self.animal_info_frame, textvariable=self.animal_name, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Tierart
        ttk.Label(self.animal_info_frame, text="Animal Type:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=(10, 0), pady=5)
        self.type_combobox = ttk.Combobox(self.animal_info_frame, textvariable=self.animal_type, values=["Cat"], width=28)
        self.type_combobox.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.type_combobox.state(["readonly"])

        # Tier-Info-Frame beim Start ausblenden
        self.animal_info_frame.grid_remove()

        # Button-Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=4, column=0)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Such-Button
        self.search_button = ttk.Button(self.button_frame, text="Search")
        self.search_button.grid(row=0, column=0, padx=10)
        self.search_button.bind("<Button-1>", lambda e: self.start_search())

        # Abbrechen-Button
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", state="disabled")
        self.cancel_button.grid(row=0, column=1, padx=10)
        self.cancel_button.bind("<Button-1>", lambda e: self.cancel_search())

        # Speichern-Button (zu Beginn deaktiviert)
        self.save_button = ttk.Button(self.button_frame, text="Save Animal", state="disabled")
        self.save_button.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        self.save_button.bind("<Button-1>", lambda e: self.save_animal())

        # Abbrechen-Button (unten rechts)
        self.exit_button = ttk.Button(self, text="Close")
        self.exit_button.grid(row=5, column=0, pady=(20, 10), sticky="e")
        self.exit_button.bind("<Button-1>", lambda e: self.exit_to_main())

        # Weiter-Button (zuerst versteckt)
        self.continue_button = ttk.Button(self, text="Continue", state="disabled")
        self.continue_button.grid(row=5, column=0, pady=(20, 10))
        self.continue_button.grid_remove()  # Weiter-Button verstecken
        self.continue_button.bind("<Button-1>", lambda e: self.exit_to_main())

        # Fortschrittsanzeige
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.grid(row=6, column=0, sticky="ew", padx=20, pady=10)

        # Liste der gespeicherten Tiere
        self.saved_animals_list = ttk.Treeview(self, columns=("name", "type", "rfid"), show="headings")
        self.saved_animals_list.heading("name", text="Name")
        self.saved_animals_list.heading("type", text="Type")
        self.saved_animals_list.heading("rfid", text="RFID")
        self.saved_animals_list.grid(row=7, column=0, sticky="nsew", padx=20, pady=10)
        self.saved_animals_list.grid_remove()  # Zuerst verborgen

    def on_click(self, event):
        if self.keyboard_visible and not self.is_within_keyboard(event):
            self.hide_keyboard()

    def is_within_keyboard(self, event):
        x, y, width, height = self.VKeyboard.winfo_x(), self.VKeyboard.winfo_y(), self.VKeyboard.winfo_width(), self.VKeyboard.winfo_height()
        return x <= event.x <= x + width and y <= event.y <= y + height

    def hide_keyboard(self):
        self.VKeyboard.grid_remove()  
        self.keyboard_visible = False  
        self.show_buttons()  
    def show_keyboard(self):
        if not self.keyboard_visible: 
            self.VKeyboard.grid() 
            self.keyboard_visible = True  
            self.hide_buttons()  

    def start_search(self):
        if not self.searching:
            self.searching = True
            self.search_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.animal_rfid.set("Searching for RFID...")
            self.progress.start()
            threading.Thread(target=self.search_animal, daemon=True).start()

    def cancel_search(self):
        self.searching = False
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.animal_rfid.set("")
        self.progress.stop()
        self.save_button.config(state="disabled")
        self.animal_info_frame.grid_remove()  

    def search_animal(self):
        while self.searching:
            rfid = getRFID()
            print(f"RFID detected: {rfid}")  
            
            if rfid is not None:
                self.animal_rfid.set(f"RFID Found: {rfid}")
                self.progress.stop()
                self.searching = False
                self.search_button.config(state="normal")
                self.cancel_button.config(state="disabled")
                self.animal_info_frame.grid()  
                self.show_keyboard()  
                break
            else:
                self.animal_rfid.set("Searching for RFID...")
            
            time.sleep(0.5)

        if self.searching:
            self.cancel_search()

    def hide_buttons(self):
        self.button_frame.grid_remove() 

    def show_buttons(self):
        self.button_frame.grid()  

    def on_name_change(self, *args):
        if self.animal_name.get().strip():
            self.save_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")

    def save_animal(self):
        name = self.animal_name.get()
        animal_type = self.animal_type.get()
        rfid = self.animal_rfid.get()

        if name and animal_type and rfid:
            self.saved_animals.append((name, animal_type, rfid))
            self.update_saved_animals_list()

            self.continue_button.grid()
            self.continue_button.config(state="normal")

            self.show_buttons() 
        else:
            
            error_message = "Please fill in all fields before saving."
            ttk.Label(self, text=error_message, foreground="red").grid(row=8, column=0, pady=(0, 10))

    def update_saved_animals_list(self):
        self.saved_animals_list.delete(*self.saved_animals_list.get_children())
        for animal in self.saved_animals:
            self.saved_animals_list.insert("", "end", values=animal)
        self.saved_animals_list.grid()  

    def exit_to_main(self):
        self.controller.show_frame("Overview")
