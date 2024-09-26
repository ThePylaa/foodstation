import tkinter as tk
from tkinter import ttk
import time

class WifiSetupSuccess(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Set background color
        self.configure(bg="#f0f0f0")
        
        # Create a style object
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("TLabel", font=controller.main_font, background="#f0f0f0", foreground="#333333")
        style.configure("TButton", font=controller.main_font, background="#4CAF50", foreground="white", padding=(10, 5))
        style.map("TButton", background=[('active', '#45a049')])
        
        # Main label
        label = ttk.Label(self, text="Network connection established", style="TLabel")
        label.pack(side="top", fill="x", pady=(30, 20), padx=290)
        
        # Register button
        register_button = ttk.Button(self, text="Register Station", command=self.register_with_animation, style="TButton")
        register_button.pack(pady=10)
        
        # Close button
        close_button = ttk.Button(self, text="Close", command=self.close_with_animation, style="TButton")
        close_button.pack(pady=10)
        
    def register_with_animation(self):
        self.animate_button(lambda: self.controller.show_frame("RegisterStation"))
        
    def close_with_animation(self):
        self.animate_button(self.controller.destroy)
        
    def animate_button(self, callback):
        def _animate():
            for i in range(5):
                self.configure(bg=f"#{15*i:02x}{15*i:02x}{15*i:02x}")
                self.update()
                time.sleep(0.05)
            self.configure(bg="#f0f0f0")
            self.update()
            callback()
        
        self.after(0, _animate)