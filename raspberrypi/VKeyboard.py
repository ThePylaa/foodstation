import tkinter as tk

class VKeyboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Speichere den Parent und initialisiere Tastatur
        self.parent = parent
        self.create()
        
        # Flag für Großbuchstaben
        self.uppercase = False

        # Event Binding für den Parent
        parent.bind_all('<FocusIn>', self.on_event, add='+')
        parent.bind_all('<Button-1>', self.on_event, add='+')

    def on_event(self, event):
        w = event.widget
        
        # Verarbeite das eigene Button nicht
        if w.master is not self:
            w_class_name = w.winfo_class()
            
            if w_class_name == 'Entry':
                self.entry = w  # Speichert das Entry-Widget
                self.grid()  # Zeigt das Keyboard an, wenn ein Entry den Fokus hat
                
            elif w_class_name == 'Button':
                self.withdraw()
                w.focus_force()

    def select(self, entry, value):
        if value == "Space":
            value = ' '
        elif value == '↓':
            self.hide_keyboard()
            self.show_buttons() 
            return  

        if value == "<-":
            if isinstance(entry, tk.Entry):
                entry.delete(len(entry.get()) - 1, 'end')
            elif isinstance(entry, tk.Text):
                entry.delete('end - 2c', 'end')
        elif value in ('Caps Lock', 'Shift'):
            self.uppercase = not self.uppercase  # Umschalten der Großbuchstaben
        else:
            if self.uppercase:
                value = value.upper()
            entry.insert('end', value)

    def create(self):
        alphabets = [
            ['=', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '[', ']'],
            ['@', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '-', '<-'],
            ['Caps Lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '\\'],
            ['Shift', '/', 'z', 'x', 'c', 'v', 'Space', 'b', 'n', 'm', ',', '.', "↓"]
        ]

        # Erstelle das Keyboard-Layout mit grid
        for y, row in enumerate(alphabets):
            x = 0
            # Füge 4 Zeilen (Offset) hinzu, um die Tastatur nach oben zu verschieben
            offset = 4  # Anzahl der Zeilen nach oben
            for text in row:
                if text in ('Enter', 'Shift', 'Space'):
                    width = 4
                    columnspan = 1
                elif text == 'Caps Lock':
                    width = 6
                    columnspan = 1
                else:
                    width = 3
                    columnspan = 1

                # Erstelle die Tasten mit Text auf den Tasten
                button = tk.Button(
                    self, text=text, width=width, 
                    bd=12, bg="black", fg="white", takefocus=False,
                    command=lambda val=text: self.select(self.entry, val)  # Taste belegen
                )
                button.grid(row=y + offset, column=x, columnspan=columnspan, padx=2, pady=2)  

                x += columnspan

        self.grid_remove()  # Verstecke das Keyboard zunächst

    def hide_keyboard(self):
        self.grid_remove()  # Versteckt die Tastatur
