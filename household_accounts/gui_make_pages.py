import csv
import datetime
import os
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


    def change_page(self):
        self.next_page = tk.Frame()
        self.next_page.grid(row=0, column=0, sticky="nsew")
        self.next_page.tkraise()


    def next_receipt(self, receipt_no):
        self.change_page()
        next_receipt_no = receipt_no + 1
        next_ocr_result = self.ocr_result[self.input_path_list[next_receipt_no]]
        next_input_file = self.input_path_list[next_receipt_no]
        gui_each_receipt.main(next_ocr_result, next_input_file, self.next_page, self, self.input_path_list)
    

    def last_page(self):
        self.change_page()
        today = datetime.datetime.now().strftime('%Y%m%d')
        csv_path = 'csv/{}.csv'.format(today)
        message = '終了しました。読み取ったデータは{}に保存されています。'.format(csv_path)
        message_label = tk.Label(self.next_page, text=message)
        message_label.pack()
        close_button = tk.Button(self.next_page, text='閉じる', command=self.destroy)
        close_button.pack()
