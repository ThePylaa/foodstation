import tkinter as tk
from tkinter import font as tkfont
from tkinter import *
from ui.welcomePage import WelcomePage
from ui.wifiSetup import WifiSetup
from ui.wifiSetupErrorPage import WifiSetupErrorPage
from ui.wifiSetupSuccess import WifiSetupSuccess
from ui.registerStation import RegisterStation
from ui.registerStationErrorPage import RegisterStationErrorPage
from ui.registerStationSuccess import RegisterStationSuccess
from ui.overview import Overview


class MainApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.after(4000, self.attributes, '-fullscreen', True)
        
        self.main_font = tkfont.Font(family='Helvetica', size=14, weight="normal")

        # Container for stacking frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames
        self.frames = {}

        # for F in (WelcomePage, WifiSetup, WifiSetupErrorPage, WifiSetupSuccess, RegisterStation, RegisterStationErrorPage):
        for F in (WelcomePage, WifiSetup, WifiSetupErrorPage, WifiSetupSuccess, RegisterStation, RegisterStationErrorPage, RegisterStationSuccess, Overview):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Virtual keyboard setup (initially hidden)
        self.keyboard_shift = False
        self.keyboard_frame = tk.Frame(self, bg="lightgray")
        self.keyboard_frame.pack(side="bottom", fill="x")
        self.create_keyboard()

        # Show welcome page
        self.show_frame("WelcomePage")
        self.hide_keyboard()

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()

    def create_keyboard(self):
        """Creates the virtual keyboard layout"""
        keyboard_buttons = [
            ["!", '"', "#", "$", "@", "&", "/", "(", ")", "?"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "Hide"],
            ["Shift", "y", "x", "c", "⌴", "v", "b", "n", "m", "DEL"]
            
        ]


        for row, key_list in enumerate(keyboard_buttons):
            for col, key in enumerate(key_list):
                if key == "Shift":
                    button = tk.Button(self.keyboard_frame, text=key, font=self.main_font,
                                       command=lambda key=key: self.handle_keyboard_input(key),
                                       width=3, height=1, bg="lightgray")
                elif key == "DEL":
                    button = tk.Button(self.keyboard_frame, text=key, font=self.main_font,
                                       command=lambda key=key: self.handle_keyboard_input(key),
                                       width=3, height=1, bg="lightgray")
                elif key == "Hide":
                    button = tk.Button(self.keyboard_frame, text=key, font=self.main_font,
                                       command=lambda key=key: self.handle_keyboard_input(key),
                                       width=3, height=1, bg="lightgray")
                elif key == "⌴":
                    button = tk.Button(self.keyboard_frame, text=key, font=self.main_font,
                                        command=lambda key=key: self.handle_keyboard_input(key),
                                        width=6, height=1, bg="white")
                else:
                    button = tk.Button(self.keyboard_frame, text=key, font=self.main_font,
                                    command=lambda key=key: self.handle_keyboard_input(key),
                                    width=3, height=1, bg="white")
                button.grid(row=row, column=col, padx=2, pady=2)

    def show_keyboard(self):
        """Shows the virtual keyboard"""
        self.keyboard_frame.pack(side="bottom", fill="x")
    
    def hide_keyboard(self):
        """Hides the virtual keyboard"""
        self.keyboard_frame.pack_forget()

    def handle_keyboard_input(self, key):
        """Handles input from the virtual keyboard"""

        #char map for special characters which get swapped on shift
        special_chars = {
            "!": "*",
            '"': "-",
            "#": "_",
            "$": "+",
            "@": "=",
            "&": "<",
            "/": ">",
            "(": "%",
            ")": "^",
            "?": "`",
        }
        
        active_entry = self.focus_get()
        if active_entry:
            if key == "DEL":
                active_entry.delete(len(active_entry.get())-1, tk.END)
            elif key == "Hide":
                self.hide_keyboard()
            elif key == "Shift":
                self.switch_keyboard_on_shift()
                self.keyboard_shift = not self.keyboard_shift
            elif key == "⌴":
                active_entry.insert(tk.END, " ")
            else:
                if self.keyboard_shift:
                    if key in special_chars:
                        key = special_chars[key]
                    else:
                        key = key.upper()
                active_entry.insert(tk.END, key)
    
    def switch_keyboard_on_shift(self):
        """Switches the case of the virtual keyboard buttons"""
        #char map for special characters
        specialchar_map = {
            "!": "*",
            '"': "-",
            "#": "_",
            "$": "+",
            "@": "=",
            "&": "<",
            "/": ">",
            "(": "%",
            ")": "^",
            "?": "`",
            "*": "!",
            "-": '"',
            "_": "#",
            "+": "$",
            "=": "@",
            "<": "&",
            ">": "/",
            "%": "(",
            "^": ")",
            "`": "?"
        }

        
        # Get all buttons from the keyboard frame
        buttons = self.keyboard_frame.winfo_children()

        # Iterate through each button
        for button in buttons:
            # Convert existing text to a list of characters
            chars = list(button['text'])

            # exclude special buttons
            if button['text'] in ["Shift", "DEL", "Hide", "Space"]:
                continue

            # Toggle the case of each character
            chars = [specialchar_map.get(char, char.upper() if char.islower() else char.lower()) if char.isalpha() else specialchar_map.get(char, char) for char in chars]
                
            # Rebuild the text and update the button label
            button['text'] = ''.join(chars)            
    

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
