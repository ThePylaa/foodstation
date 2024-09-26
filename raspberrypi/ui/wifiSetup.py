import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
import subprocess
import os
from raspberryUtils import hasInternet
import time
import threading

class WifiSetup(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def show_keyboard(self):
        # Start the matchbox keyboard
        self.keyboard_process = subprocess.Popen(["matchbox-keyboard"])
    
    def hide_keyboard(self):
        # Kill the matchbox keyboard process
        subprocess.run(["pkill", "matchbox-keyboard"])
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        title = ttk.Label(self, text="Wi-Fi Setup", font=("Helvetica", 24, "bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Status message
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var, font=("Helvetica", 14))
        self.status_label.grid(row=1, column=0, pady=(0, 10))

        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Network list label
        network_label = ttk.Label(content_frame, text="Available Networks:", font=("Helvetica", 14))
        network_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Network list with scrollbar
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self.network_list = ttk.Treeview(list_frame, columns=("ssid",), show="headings", selectmode="browse")
        self.network_list.heading("ssid", text="SSID")
        self.network_list.column("ssid", width=200)
        self.network_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.network_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.network_list.configure(yscrollcommand=scrollbar.set)

        # Password entry
        password_frame = ttk.Frame(content_frame)
        password_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        password_frame.grid_columnconfigure(1, weight=1)

        password_label = ttk.Label(password_frame, text="Password:", font=("Helvetica", 12))
        password_label.grid(row=0, column=0, padx=(0, 10))

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=0, column=1, sticky="ew")
        
        # Bind focus events to show/hide the on-screen keyboard
        self.password_entry.bind("<FocusIn>", lambda event: self.controller.show_keyboard())
        self.password_entry.bind("<FocusOut>", lambda event: self.controller.hide_keyboard())

        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, pady=(20, 10))

        self.refresh_button = ttk.Button(button_frame, text="Refresh Networks", command=self.update_networks, bootstyle="info")
        self.refresh_button.grid(row=0, column=0, padx=5)

        self.connect_button = ttk.Button(button_frame, text="Connect", command=self.connect_to_selected_wifi, bootstyle="success")
        self.connect_button.grid(row=0, column=1, padx=5)

        self.disconnect_button = ttk.Button(button_frame, text="Disconnect", command=self.disconnect_from_wifi, bootstyle="warning")
        self.disconnect_button.grid(row=0, column=2, padx=5)

        back_button = ttk.Button(self, text="Go Back", command=lambda: self.controller.show_frame("Overview"), bootstyle="danger")
        back_button.grid(row=4, column=0, pady=(10, 20), sticky="se")

        # Progress bar
        self.progress = ttk.Progressbar(self, mode="indeterminate", bootstyle="primary-striped")
        self.progress.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.update_ui_for_connection_status()

    def update_ui_for_connection_status(self):
        if hasInternet():
            self.status_var.set("Connected to a network")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
        else:
            self.status_var.set("Not connected to any network")
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
        self.update_networks()

    def scan_wifi(self):
        if hasInternet():
            return ["Already connected"]

        wifi_list = []
        for i in range(3):
            try:
                networks = subprocess.check_output(["iwlist", "wlan0", "scan"])
                networks = networks.decode("utf-8").split("\n")
                for line in networks:
                    if "ESSID" in line:
                        ssid = line.split('"')[1]
                        if ssid and ssid not in wifi_list:
                            wifi_list.append(ssid)
                break
            except subprocess.CalledProcessError:
                print(f"Failed to scan networks (attempt {i+1})")
                time.sleep(1)
        return wifi_list or ["No networks found"]

    def update_networks(self):
        self.network_list.delete(*self.network_list.get_children())
        self.refresh_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("Scanning for networks...")
        self.update()

        def scan_and_update():
            new_networks = self.scan_wifi()
            self.network_list.delete(*self.network_list.get_children())
            for ssid in new_networks:
                self.network_list.insert("", "end", values=(ssid,))
            self.refresh_button.config(state="normal")
            self.progress.stop()
            self.status_var.set("Scan complete")

        threading.Thread(target=scan_and_update, daemon=True).start()

    def connect_to_selected_wifi(self):
        selection = self.network_list.selection()
        if not selection:
            self.status_var.set("Please select a network")
            return
        ssid = self.network_list.item(selection[0])['values'][0]
        password = self.password_var.get()

        if ssid == "Already connected":
            self.status_var.set("Already connected to a network")
            return

        self.progress.start()
        self.status_var.set(f"Connecting to {ssid}...")
        self.update()

        def connect():
            for i in range(3):
                os.system(f'sudo raspi-config nonint do_wifi_ssid_passphrase "{ssid}" {password}')
                time.sleep(5)  # Wait for connection attempt
                if hasInternet():
                    self.controller.show_frame("WifiSetupSuccess")
                    break
            else:
                self.controller.show_frame("WifiSetupErrorPage")
            self.progress.stop()
            self.update_ui_for_connection_status()

        threading.Thread(target=connect, daemon=True).start()

    def disconnect_from_wifi(self):
        self.progress.start()
        self.status_var.set("Disconnecting from network...")
        self.update()

        def disconnect():
            try:
                ssid = subprocess.check_output("iwgetid -r", shell=True).decode("utf-8").strip()
                subprocess.run(["sudo", "nmcli", "connection", "delete", ssid])
                time.sleep(2)  # Wait for disconnection
            except subprocess.CalledProcessError:
                pass
            self.progress.stop()
            self.update_ui_for_connection_status()

        threading.Thread(target=disconnect, daemon=True).start()