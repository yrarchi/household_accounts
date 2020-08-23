from PIL import Image
import tkinter as tk
import tkinter.ttk as ttk


class MakeGUI(tk.Tk):
    width = 1400
    height = 600
    img_width = 300
    info_height = 100
    info_width = width - img_width
    item_height = height - info_height

    def __init__(self):
        super().__init__()
        self.make_screen()
        self.img_frame, self.receipt_info_frame, self.item_frame = self.divide_screen()


    def make_screen(self):
        self.title('読み取り内容修正')
        self.geometry('{}x{}'.format(self.width, self.height))


    def divide_screen(self):
        receipt_img_frame = tk.Frame(self, width=self.img_width, height=self.height)
        receipt_img_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.N, tk.S))

        receipt_info_frame = tk.Frame(self, width=self.info_width, height=self.info_height)
        receipt_info_frame.grid(row=0, column=1)

        item_frame = tk.Frame(self, width=self.info_width, height=self.item_height)
        item_frame.grid(row=1, column=1)

        return receipt_img_frame, receipt_info_frame, item_frame


class ReceiptInfoFrame():
    column_list = ['日付', '店舗', '内税/外税']
    shop_list = ['店舗', 'コンビニ']  # あとでDBから引っ張るようにする

    def __init__(self, frame, read_date):
        self.show_info(frame, read_date)

    def show_info(self, frame, read_date):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(frame, text=text)
            date_label.grid(row=0, column=column)

        date_box = tk.Entry(frame)
        date_box.insert(tk.END, read_date)
        date_box.grid(row=1, column=0)

        shop = ttk.Combobox(frame)
        shop['values'] = self.shop_list
        shop.grid(row=1, column=1)

        tax_in = tk.Radiobutton(frame, text='内税', value='in')
        tax_ex = tk.Radiobutton(frame, text='外税', value='ex')
        tax_in.grid(row=1, column=2)
        tax_ex.grid(row=1, column=3)


class ImgFrame():
    def __init__(self, frame, width, height, input_file):
        self.width = width
        self.height = height
        self.show_img(frame, input_file)


    def convert_jpg_to_png(self, input_file, img):
        png_input_file = input_file[:-4] + '.png'
        img.save(png_input_file)
        return png_input_file


    def resize_img(self, input_file, img):
        img_width, img_height = img.size
        rate_width = img_width / self.width
        rate_height = img_height / self.height
        if abs(rate_width-1) >= abs(rate_height-1):
            resize_img = img.resize((self.width, int(img_height/rate_width)))
        else:
            resize_img = img.resize((int(img_width/rate_height), self.height))
        resize_input_file = input_file[:-4] + '_resize' + '.png'
        resize_img.save(resize_input_file)
        return resize_input_file


    def show_img(self, frame, input_file):
        canvas = tk.Canvas(frame, bg='black', width = self.width, height = self.height)
        img = Image.open(input_file)
        if input_file[-4:] != '.png':
            input_file = self.convert_jpg_to_png(input_file, img)
        resize_input_file = self.resize_img(input_file, img)
        self.img = tk.PhotoImage(file = resize_input_file)
        canvas.create_image(0, 0, anchor='nw', image=self.img)
        canvas.pack(expand = True, fill = tk.BOTH)


class ItemFrame():
    major_category_list = ['食費', '光熱費']  # todo: DBから引っ張るようにする
    medium_category_list = ['野菜', '米']  # todo: DBから引っ張るようにする
    column_list = ['品目', '金額', '大項目', '中項目', '軽減税率', '付帯費', '付帯費内容', '特別費']
        
    def __init__(self, frame, read_item, read_price, read_redued_tax_rate):
        self.frame = frame
        self.show_item_column()
        self.show_read_items(read_item, read_price, read_redued_tax_rate)


    def show_item_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)
    

    def show_item_value(self, row, read_item, read_price, read_reduced_tax_rate):
        item_box = tk.Entry(self.frame, width=25)
        item_box.insert(tk.END, read_item)
        item_box.grid(row=row, column=0)

        price_box = tk.Entry(self.frame, width=5)
        price_box.insert(tk.END, read_price)
        price_box.grid(row=row, column=1)

        major_category = ttk.Combobox(self.frame, width=12)
        major_category['values'] = self.major_category_list
        major_category.grid(row=row, column=2)

        medium_category = ttk.Combobox(self.frame, width=12)
        medium_category['values'] = self.medium_category_list
        medium_category.grid(row=row, column=3)

        self.CheckVar = tk.IntVar(value=read_reduced_tax_rate)
        reduced_tax_rate = ttk.Checkbutton(self.frame, variable=self.CheckVar)
        reduced_tax_rate.grid(row=row, column=4)

        extra_cost = tk.Entry(self.frame, width=5)
        extra_cost.insert(tk.END, '')
        extra_cost.grid(row=row, column=5)

        extra_cost_detail = tk.Entry(self.frame, width=7)
        extra_cost_detail.insert(tk.END, '')
        extra_cost_detail.grid(row=row, column=6)

        self.CheckVar = tk.IntVar(value=0)  # デフォルトオフ
        special_cost = ttk.Checkbutton(self.frame, variable=self.CheckVar)
        special_cost.grid(row=row, column=7)
    

    def show_read_items(self, read_item, read_price, read_redued_tax_rate):
        for row, (item, price, redued_tax_rate) in enumerate(zip(read_item, read_price, read_redued_tax_rate)):
            self.show_item_value(row+1, item, price, redued_tax_rate)


def main(read_date, read_item, read_price, read_reduced_tax_rate, input_file):
    gui = MakeGUI()
    receipt_info_frame = ReceiptInfoFrame(gui.receipt_info_frame, read_date)
    img_frame = ImgFrame(gui.img_frame, gui.img_width, gui.height, input_file)
    item_frame = ItemFrame(gui.item_frame, read_item, read_price, read_reduced_tax_rate)
    gui.mainloop()


if __name__ == '__main__':
    main()