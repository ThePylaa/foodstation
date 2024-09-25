import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
import requests
import json
from VKeyboard import VKeyboard

class RegisterStation(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        with open("/home/pi/Desktop/feedingstation/raspberrypi/config.json", "r") as file:
            self.config = json.loads(file.read())
        self.api_host = self.config["API_HOST"]

        self.station_name = tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()

        self.create_widgets()
        self.VKeyboard = VKeyboard(self)

        self.keyboard_visible = False

        # Bind events to show/hide keyboard
        self.bind_all('<FocusIn>', self.on_focus_in)
        self.bind_all('<Button-1>', self.on_click)

        # Track changes in input fields
        self.station_name.trace_add("write", self.check_fields)
        self.email.trace_add("write", self.check_fields)
        self.password.trace_add("write", self.check_fields)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Title
        title = ttk.Label(self, text="Register Station", font=("Helvetica", 24, "bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Instructions
        instructions = ttk.Label(self, text="Please fill in the details to register your station",
                                 font=("Helvetica", 14))
        instructions.grid(row=1, column=0, pady=(0, 20))

        # Registration Form Frame
        self.registration_frame = ttk.Frame(self)
        self.registration_frame.grid(row=2, column=0, pady=(0, 20), sticky="nsew")
        self.registration_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.registration_frame, text="Station Name:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(10, 0), pady=5)
        self.name_entry = ttk.Entry(self.registration_frame, textvariable=self.station_name, width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.name_entry.bind("<FocusIn>", self.on_entry_focus)

        ttk.Label(self.registration_frame, text="Email:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=(10, 0), pady=5)
        self.email_entry = ttk.Entry(self.registration_frame, textvariable=self.email, width=30)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.email_entry.bind("<FocusIn>", self.on_entry_focus)

        ttk.Label(self.registration_frame, text="Password:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=(10, 0), pady=5)
        self.password_entry = ttk.Entry(self.registration_frame, textvariable=self.password, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.password_entry.bind("<FocusIn>", self.on_entry_focus)

        # Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=3, column=0)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Register Button
        self.register_button = ttk.Button(self.button_frame, text="Register", command=self.register_station, state="disabled")  # Initially disabled
        self.register_button.grid(row=0, column=0, padx=10)

        # Close Button
        self.close_button = ttk.Button(self.button_frame, text="Close")
        self.close_button.grid(row=0, column=1, padx=10)
        self.close_button.bind("<Button-1>", lambda e: self.exit_to_main())

    def check_fields(self, *args):
        """Enable the Register button only if all fields are filled."""
        if self.station_name.get() and self.email.get() and self.password.get():
            self.register_button.config(state="normal")  # Enable button
        else:
            self.register_button.config(state="disabled")  # Disable button

    def on_entry_focus(self, event):
        self.current_entry = event.widget
        self.show_keyboard()

    def on_focus_in(self, event):
        if event.widget in (self.name_entry, self.email_entry, self.password_entry):
            self.show_keyboard()
            self.VKeyboard.entry = event.widget

    def on_click(self, event):
        if self.keyboard_visible and not self.is_within_keyboard(event):
            self.hide_keyboard()
        elif isinstance(event.widget, ttk.Entry):
            self.current_entry = event.widget
            self.show_keyboard()

    def is_within_keyboard(self, event):
        if not self.keyboard_visible:
            return False
        x, y = event.x_root, event.y_root  # Use root coordinates
        keyboard_x = self.VKeyboard.winfo_rootx()
        keyboard_y = self.VKeyboard.winfo_rooty()
        keyboard_width = self.VKeyboard.winfo_width()
        keyboard_height = self.VKeyboard.winfo_height()
        return keyboard_x <= x <= keyboard_x + keyboard_width and keyboard_y <= y <= keyboard_y + keyboard_height

    def show_keyboard(self):
        if not self.keyboard_visible:
            self.VKeyboard.grid(row=4, column=0)
            self.keyboard_visible = True
            self.hide_buttons()
        self.VKeyboard.entry = self.current_entry

    def hide_keyboard(self):
        self.VKeyboard.grid_remove()
        self.keyboard_visible = False
        self.show_buttons()

    def hide_buttons(self):
        self.button_frame.grid_remove()

    def show_buttons(self):
        self.button_frame.grid()

    def register_station(self):
        if self.register_button['state'] == 'disabled':
            return  # Prevent the function from running if the button is disabled
        
        self.hide_keyboard()
        print("Registering station")
        station_name = self.station_name.get()
        email = self.email.get()
        password = self.password.get()
        api_host = self.api_host
        config = self.config

        try:
            loginRes = requests.post(f"{api_host}/user/login", json={"email": email, "password": password})
            
            if loginRes.status_code != 200:
                self.controller.show_frame("RegisterStationErrorPage")
                return
            
            loginRes = loginRes.json()
            user_id = loginRes["user_id"]
            config["USER_ID"] = user_id

            station_id = requests.get(f"{api_host}/feedingstation/new_station_uuid")
            station_id = station_id.json()

            registerRes = requests.post(f"{api_host}/feedingstation/register", json={"feedingstation_id": station_id, "user_id": user_id, "name": station_name})

            if registerRes.status_code == 200:
                config["DEVICE_UUID"] = station_id
                config["DEVICE_NAME"] = station_name
                with open("/home/pi/Desktop/feedingstation/raspberrypi/config.json", "w") as file:
                    file.write(json.dumps(config))

                self.controller.show_frame("RegisterStationSuccess")
            else:
                self.controller.show_frame("RegisterStationErrorPage")
        except:
            self.controller.show_frame("RegisterStationErrorPage")
    
    def exit_to_main(self):
        self.controller.show_frame("Overview")