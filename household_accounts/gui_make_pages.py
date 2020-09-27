import tkinter as tk


class MakePages(tk.Tk):
    width = 1400
    img_width = 300
    info_width = width - img_width
    height = 600
    info_height = 60
    operation_height = 100
    item_height = height - info_height - operation_height


    def __init__(self):
        super().__init__()
        self.make_screen()
        self.make_pages()
        change_page(self.page1)


    def make_screen(self):
        self.title('読み取り内容修正')
        self.geometry('{}x{}'.format(self.width, self.height))


    def make_pages(self):
        self.page1 = tk.Frame()
        self.page1.grid(row=0, column=0, sticky="nsew")
        self.page2 = tk.Frame()
        self.page2.grid(row=0, column=0, sticky="nsew")


def change_page(page):
    page.tkraise()