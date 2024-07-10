import tkinter as tk
import requests
import json

class RegisterStation(tk.Frame):
    def __init__(self, parent, controller):
        with open("/home/pi/Desktop/feedingstation/raspberrypi/config.json", "r") as file:
            self.config = json.loads(file.read())
        self.api_host= self.config["API_HOST"]
            
        tk.Frame.__init__(self, parent)
        self.controller = controller

        try:
            isExistingRes = requests.get(f"{self.api_host}/feedingstation/info?feedingstation_id={self.config['DEVICE_UUID']}")
            if isExistingRes.status_code == 200:
                self.label = tk.Label(self, text="Station already registered", font=controller.main_font)
                self.label.pack(side="top", fill="x", pady=10)
                self.label = tk.Label(self, text="Station Name: " + self.config["DEVICE_NAME"], font=controller.main_font)
                self.label.pack(side="top", fill="x", pady=10)
                self.label = tk.Label(self, text="Station ID: " + self.config["DEVICE_UUID"], font=controller.main_font)
                self.label.pack(side="top", fill="x", pady=10)

                self.continue_button = tk.Button(self, text="Continue", font=controller.main_font, command=lambda: controller.show_frame("Overview"))
                self.continue_button.pack()
                return
        except:
            pass
        

        self.label = tk.Label(self, text="Register Station", font=controller.main_font)
        self.label.pack(side="top", fill="x", pady=10)

        self.station_name_label = tk.Label(self, text="Station Name", font=controller.main_font)
        self.station_name_label.pack()
        self.station_name_entry = tk.Entry(self, font=controller.main_font)
        self.station_name_entry.pack()
        self.station_name_entry.bind("<FocusIn>", lambda event: controller.show_keyboard())
        self.station_name_entry.bind("<FocusOut>", lambda event: controller.hide_keyboard())

        self.email_label = tk.Label(self, text="Email", font=controller.main_font)
        self.email_label.pack()
        self.email_entry = tk.Entry(self, font=controller.main_font)
        self.email_entry.pack()
        self.email_entry.bind("<FocusIn>", lambda event: controller.show_keyboard())
        self.email_entry.bind("<FocusOut>", lambda event: controller.hide_keyboard())

        self.password_label = tk.Label(self, text="Password", font=controller.main_font)
        self.password_label.pack()
        self.password_entry = tk.Entry(self, font=controller.main_font, show="*")
        self.password_entry.pack()
        self.password_entry.bind("<FocusIn>", lambda event: controller.show_keyboard())
        self.password_entry.bind("<FocusOut>", lambda event: controller.hide_keyboard())

        self.register_button = tk.Button(self, text="Register", font=controller.main_font, command=lambda: self.register_station())
        self.register_button.pack()

        #debug button to show the next page, placed at the right top corner
        debug_button = tk.Button(self, text="Close", command=lambda: controller.destroy(), pady=10, background="grey", foreground="white", font=controller.main_font)
        debug_button.place(relx=1.0, rely=0.0, anchor="ne")

    def register_station(self):
        self.controller.hide_keyboard()
        print("Registering station")
        station_name = self.station_name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
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
