import tkinter as tk
import gui_each_receipt

class MakePages(tk.Tk):
    width = 1400
    img_width = 300
    info_width = width - img_width
    height = 600
    info_height = 60
    operation_height = 100
    item_height = height - info_height - operation_height


    def __init__(self, num_receipts, input_path_list, ocr_result):
        super().__init__()
        self.input_path_list = input_path_list
        self.ocr_result = ocr_result
        self.make_screen()
        self.make_page1()


    def make_screen(self):
        self.title('読み取り内容修正')
        self.geometry('{}x{}'.format(self.width, self.height))


    def make_page1(self):
        self.page1 = tk.Frame()
        self.page1.grid(row=0, column=0, sticky="nsew")


    def next_receipt(self, input_file):
        next_receipt_no = self.input_path_list.index(input_file) + 1 if input_file != 0 else 0
        self.next_page = tk.Frame()
        self.next_page.grid(row=0, column=0, sticky="nsew")
        self.next_page.tkraise()
        next_ocr_result = self.ocr_result[self.input_path_list[next_receipt_no]]
        next_input_file = self.input_path_list[next_receipt_no]
        gui_each_receipt.main(next_ocr_result, next_input_file, self.next_page, self)