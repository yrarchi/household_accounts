import tkinter as tk
from PIL import Image

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
        input_path = './img/interim/write_contours_IMG_7434.png'
        resize_file_path = resize_img(input_path, resize_width=self.width, resize_height=self.height-100)
        img = tk.PhotoImage(file = resize_file_path)
        
        canvas = tk.Canvas(self.page1, bg='black', width=self.width, height=self.height-100)
        canvas.create_image(0, 0, image=img, anchor='nw')
        canvas.grid(row=1, column=0)

        self.change_pageButton = tk.Button(self.page1, text="各レシートの読み取りへ進む → ", command=lambda : change_page(self.page2))
        self.change_pageButton.grid(row=2, column=0)

    

"""        interim_relative_path = '../img/interim'
        interim_path = os.path.join(os.path.dirname(__file__), interim_relative_path)
        self.input_filename = os.path.splitext(os.path.basename(input_path))[0]

        cv2.imwrite('{}/write_contours_{}.png'.format(self.interim_path, self.input_filename), draw_contours_file)
"""