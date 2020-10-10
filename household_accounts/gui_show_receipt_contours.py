import tkinter as tk
from PIL import Image

import config
from get_file_path_list import get_input_path_list
from gui_make_pages import MakePages
from resize_image import resize_img


class MakePage1():
    width = config.width
    height = config.height

    def __init__(self, gui):
        self.page = gui.page1
        self.show_receipt_contours(gui)


    def show_receipt_contours(self, gui):
        self.titleLabel = tk.Label(self.page, text='レシート検知結果')
        self.titleLabel.pack()

        global img
        input_path_list = get_input_path_list(relative_path='../img/interim', extension='png')
        input_path = [f for f in input_path_list if 'interim/write_contours_' in f][0]
        resize_file_path = resize_img(input_path, resize_width=self.width, resize_height=self.height-100)
        img = tk.PhotoImage(file = resize_file_path)

        canvas = tk.Canvas(self.page, width=self.width, height=self.height-100)
        canvas.create_image(self.width/2, (self.height-100)/2, image=img, anchor='center')
        canvas.pack(anchor='center')

        self.change_pageButton = tk.Button(self.page, text='各レシートの読み取りへ進む → ', command=lambda : MakePages.next_receipt(gui, 0))
        self.change_pageButton.pack(anchor='s', ipadx=100, ipady=15, padx=50)