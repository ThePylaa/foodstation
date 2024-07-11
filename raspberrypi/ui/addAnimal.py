import tkinter as tk
from arduinoCommunication import getRFID
import time

class AddAnimal(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        animal_rfid = None

        self.label = tk.Label(self, text="Add an Animal", font=controller.main_font)
        self.label.pack(side="top", fill="x", pady=10)

        self.serach_button = tk.Button(self, text="Search", font=controller.main_font, command=lambda: animal_rfid = self.search_animal())
        self.serach_button.pack()

        self.debug_button = tk.Button(self, text="Go Back", font=controller.main_font, command=lambda: controller.show_frame("Overview"))
        self.debug_button.place(relx=1.0, rely=0.0, anchor="ne")

    def search_animal(self):
        rfid = getRFID()
        while rfid is "----NORFID----":
            rfid = getRFID()
            time.sleep(0.3)
        return rfid
        