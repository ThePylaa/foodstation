import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
from arduinoCommunication import dispensePortion
from VKeyboard import VKeyboard

class Overview(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent  # Speichere die Referenz auf das Hauptfenster

        # Übersicht-Label
        self.label = ttk.Label(self, text="Overview", font=("Helvetica", 24, "bold"))
        self.label.grid(row=0, sticky="ew", pady=20, padx=325)

        # Frame für Buttons erstellen und konfigurieren
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, sticky="nsew")

        buttons = [
            ("Welcome", lambda: controller.show_frame("WelcomePage")),
            ("Wifi Setup", lambda: controller.show_frame("WifiSetup")),
            ("Register Station", lambda: controller.show_frame("RegisterStation")),
            ("Add Animal", lambda: controller.show_frame("AddAnimal")),
            ("Dispense a Portion", lambda: dispensePortion(1))
        ]

        for row_index, (text, command) in enumerate(buttons):
            btn = ttk.Button(frame, text=text, command=command)
            btn.grid(row=row_index, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        # Configure rows and columns for the grid
        for row_index in range(5):
            frame.grid_rowconfigure(row_index, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Close Button
        close_button = ttk.Button(self, text="Close", bootstyle="danger", command=self.close_program)
        close_button.grid(row=2, column=0, pady=20, sticky="ew")

    def close_program(self):
        print("Closing program...")
        self.parent.quit()  # Beendet die mainloop
        self.parent.destroy()  # Schließt das Fenster

if __name__ == "__main__":
    root = tk.Tk()
    app = Overview(root, None)
    app.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()
