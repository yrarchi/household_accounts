import tkinter as tk

import config
from get_file_path_list import get_input_path_list


class MakeGuiScreen(tk.Tk):
    width = config.width
    height = config.height

    def __init__(self, ocr_results):
        super().__init__()
        self.input_path_list = get_input_path_list("../img/interim/each_receipt", "png")
        self.ocr_results = ocr_results
        self.make_screen()
        self.make_first_page()

    def make_screen(self):
        self.title("レシート整理")
        self.geometry("{}x{}".format(self.width, self.height))

    def make_first_page(self):
        self.first_page = tk.Frame()
        self.first_page.grid(row=0, column=0, sticky="nsew")

    def change_page(self):
        self.next_page = tk.Frame()
        self.next_page.grid(row=0, column=0, sticky="nsew")
        self.next_page.tkraise()
