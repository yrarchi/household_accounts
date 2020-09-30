import tkinter as tk
from PIL import Image

from get_file_path_list import get_input_path_list
from gui_make_pages import change_page
from resize_image import resize_img


class MakePage1():
    width = 1400
    height = 600

    def __init__(self, page1, page2):
        self.page1 = page1
        self.page2 = page2
        self.show_receipt_contours()


    def show_receipt_contours(self):
        self.titleLabel = tk.Label(self.page1, text="レシート検知結果")
        self.titleLabel.grid(row=0, column=0)

        global img
        input_path_list = get_input_path_list(relative_path='../img/interim/', extension='png')
        input_path = [f for f in input_path_list if 'interim/write_contours_' in f][0]
        resize_file_path = resize_img(input_path, resize_width=self.width, resize_height=self.height-100)
        img = tk.PhotoImage(file = resize_file_path)
        
        canvas = tk.Canvas(self.page1, bg='black', width=self.width, height=self.height-100)
        canvas.create_image(0, 0, image=img, anchor='nw')
        canvas.grid(row=1, column=0)

        self.change_pageButton = tk.Button(self.page1, text="各レシートの読み取りへ進む → ", command=lambda : change_page(self.page2))
        self.change_pageButton.grid(row=2, column=0)