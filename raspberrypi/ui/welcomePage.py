import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
from PIL import Image, ImageTk

class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        controller = self.controller  # Ensure controller is accessible within this method

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Welcome to Your Feeding Station Setup", 
                                font=("Helvetica", 24, "bold"), 
                                bootstyle="primary")
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Content frame
        content_frame = ttk.Frame(main_frame, bootstyle="light")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Logo (replace 'logo.png' with your actual logo file)
        try:
            logo = Image.open("logo.png")
            logo = logo.resize((150, 150), Image.LANCZOS)
            logo_image = ImageTk.PhotoImage(logo)
            logo_label = ttk.Label(content_frame, image=logo_image)
            logo_label.image = logo_image
            logo_label.grid(row=0, column=0, pady=(20, 10))
        except FileNotFoundError:
            print("Logo file not found. Skipping logo display.")

        # Welcome message
        message = ("Welcome to your feeding station setup!\n\n"
                   "This wizard will guide you through the process of setting up your device.\n"
                   "You'll need a Wi-Fi connection to complete this setup.\n\n"
                   "Click 'Get Started' below to begin!")
        
        message_label = ttk.Label(content_frame, text=message, 
                                  font=("Helvetica", 14),
                                  justify="center", wraplength=400)
        message_label.grid(row=1, column=0, pady=20)

        # Get Started button
        start_button = ttk.Button(content_frame, text="Get Started!", 
                                  command=lambda: self.controller.show_frame("WifiSetup"),
                                  bootstyle="success-outline", 
                                  width=20)
        start_button.grid(row=2, column=0, pady=(0, 20))