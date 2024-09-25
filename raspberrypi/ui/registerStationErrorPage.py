import tkinter as tk
from tkinter import ttk
import time

class RegisterStationErrorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Set background color
        self.configure(bg="#f0f0f0")
        
        # Create a style object
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("Danger.TLabel", font=controller.main_font, background="#f0f0f0", foreground="#333333", padding=(0, 20))
        style.configure("Danger.TButton", font=controller.main_font, background="#4CAF50", foreground="white", padding=(10, 5))
        style.map("Danger.TButton", background=[('active', '#45a049')])
        
        # Success message
        label = ttk.Label(self, text="Failed to register the station", style="Warning.TLabel")
        label.pack(side="top", fill="x", pady=(30, 20))
        
        # Add a checkmark symbol for visual confirmation
        checkmark = ttk.Label(self, text="X", font=("Arial", 48), foreground="#FF0000", background="#f0f0f0")
        checkmark.pack(pady=(0, 20))
        
        # Try again button
        overview_button = ttk.Button(self, text="Try again", command=self.show_overview_with_animation, style="Warning.TButton")
        overview_button.pack(pady=10)
        
    def show_overview_with_animation(self):
        self.animate_transition(lambda: self.controller.show_frame("RegisterStation"))
        
    def animate_transition(self, callback):
        def _animate():
            for i in range(10):
                self.configure(bg=f"#{25*i:02x}{25*i:02x}{25*i:02x}")
                self.update()
                time.sleep(0.03)
            callback()
        
        self.after(0, _animate)