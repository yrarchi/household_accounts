import csv
import datetime
import os
import tkinter as tk

import config


class MakePages(tk.Tk):
    width = config.width
    height = config.height

    def __init__(self, input_path_list, ocr_results):
        super().__init__()
        self.input_path_list = input_path_list
        self.ocr_results = ocr_results
        self.make_screen()
        self.make_page1()


    def make_screen(self):
        self.title('読み取り内容修正')
        self.geometry('{}x{}'.format(self.width, self.height))


    def make_page1(self):
        self.page1 = tk.Frame()
        self.page1.grid(row=0, column=0, sticky='nsew')


    def change_page(self):
        self.next_page = tk.Frame()
        self.next_page.grid(row=0, column=0, sticky='nsew')
        self.next_page.tkraise()