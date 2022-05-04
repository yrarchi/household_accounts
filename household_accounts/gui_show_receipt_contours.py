import tkinter as tk

import config
import gui_each_receipt
from get_file_path_list import get_input_path_list
from edit_image import resize_img


class MakeFirstPage:
    width = config.width
    height = config.height

    def __init__(self, gui):
        self.page = gui.first_page
        self.show_receipt_contours(gui)
        self.show_button_first_receipt(gui)

    def show_receipt_contours(self, gui):
        self.titleLabel = tk.Label(self.page, text="レシート検知結果")
        self.titleLabel.pack()

        global img
        input_path_list = get_input_path_list("../img/interim", "png")
        input_path = [f for f in input_path_list if "interim/write_contours_" in f][0]
        resize_file_path = resize_img(
            input_path, resize_width=self.width, resize_height=self.height - 100
        )
        img = tk.PhotoImage(file=resize_file_path)

        canvas = tk.Canvas(self.page, width=self.width, height=self.height - 100)
        canvas.create_image(
            self.width / 2, (self.height - 100) / 2, image=img, anchor="center"
        )
        canvas.pack(anchor="center")

    def show_button_first_receipt(self, gui):
        def first_receipt():
            gui.change_page()
            first_input_file = gui.input_path_list[0]
            first_ocr_result = gui.ocr_results[first_input_file]
            gui_each_receipt.main(
                first_ocr_result, first_input_file, gui.next_page, gui
            )

        self.change_pageButton = tk.Button(
            self.page, text="各レシートの読み取りへ進む → ", command=lambda: first_receipt()
        )
        self.change_pageButton.pack(anchor="s", ipadx=100, ipady=15, padx=50)
