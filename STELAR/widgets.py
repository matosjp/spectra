import ttkbootstrap as ttk
import tkinter as tk
import pickle
from tkinter import filedialog


class SessionManager:
    @staticmethod
    def save_session():
        filename = filedialog.askopenfilename(filetypes=[("Text file", "*.text"), ("All files", "*.*")])
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(SessionManager.session_data, f)

    @staticmethod
    def load_session(filename):
        with open(filename, 'rb') as f:
            SessionManager.session_data = pickle.load(f)

    @staticmethod
    def set_session_data(key, value):
        SessionManager.session_data[key] = value

    @staticmethod
    def get_session_data(key):
        return SessionManager.session_data.get(key)


class AboutWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        # Label displaying information about the program author
        author_label = tk.Label(self, text="Author: João Paulo Matos Dias Gomes")
        author_label.pack(padx=20, pady=10)

        # Label displaying program version
        version_label = tk.Label(self, text="Version: 1.0")
        version_label.pack(padx=20, pady=5)

        # Label displaying program date
        date_label = tk.Label(self, text="Date: 20/12/2024")
        date_label.pack(padx=20, pady=5)

        # Description label
        description_label = tk.Label(self,
                                     text="Description:\nS.T.E.L.A.R. (Stellar Type Examination and Analysis Resource) "
                                          "\nis a software tool designed for the comprehensive analysis of stellar "
                                          "data."
                                          "\nIt provides astronomers and astrophysicists with a suite of powerful "
                                          "algorithms"
                                          "\nfor determining various parameters related to stars, including stellar"
                                          ' type,'
                                          "\nluminosity, temperature, radius, mass, age, and distance. This program is "
                                          "\nintended for research and educational purposes, offering a user-friendly "
                                          "\ninterface and accurate analytical capabilities for studying the properties"
                                          "\nand behaviors of stars across the cosmos.")
        description_label.pack(padx=20, pady=10)


class SizeNotifier:
    def __init__(self, window, size_dict):
        self.window = window
        self.size_dict = {key: value for key, value in sorted(size_dict.items())}
        self.current_min_size = None
        self.window.bind('<Configure>', self.check_size)

        self.window.update()

        min_height = self.window.winfo_height()
        min_width = list(self.size_dict)[0]
        self.window.minsize(min_width, min_height)

    def check_size(self, event):
        if event.widget == self.window:
            window_width = event.width
            checked_size = None

            for min_size in self.size_dict:
                delta = window_width - min_size
                if delta >= 0:
                    checked_size = min_size

            if checked_size != self.current_min_size:
                self.current_min_size = checked_size
                self.size_dict[self.current_min_size]()
