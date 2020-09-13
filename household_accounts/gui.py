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

    def __init__(self, frame, read_date, tax_excluded):
        self.show_info(frame, read_date, tax_excluded)

    def show_info(self, frame, read_date, tax_excluded):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(frame, text=text)
            date_label.grid(row=0, column=column)

        date_box = tk.Entry(frame)
        date_box.insert(tk.END, read_date)
        date_box.grid(row=1, column=0)

        shop = ttk.Combobox(frame)
        shop['values'] = self.shop_list
        shop.grid(row=1, column=1)

        tax_var = tk.IntVar()
        tax_var.set(tax_excluded)
        tax_in = ttk.Radiobutton(frame, text='内税', value=0, variable=tax_var)
        tax_ex = ttk.Radiobutton(frame, text='外税', value=1, variable=tax_var)
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
    column_list = ['品目', '読み取り価格', '軽減税率', '税込価格', '大項目', '中項目', '付帯費', '付帯費内容', '特別費']
    tax_rate = 1.1
    reduced_tax_rate = 1.08

        
    def __init__(self, frame, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded):
        self.frame = frame
        self.show_item_column()
        self.show_item_value(read_item, read_price, read_reduced_tax_rate_flg)
        self.show_item_price_tax_in(read_price, read_reduced_tax_rate_flg, tax_excluded)


    def show_item_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)
    

    def show_item_value(self, read_item, read_price, read_reduced_tax_rate_flg):
        for row, (item, price, reduced_tax_rate_flg) in enumerate(zip(read_item, read_price, read_reduced_tax_rate_flg)):
            row = row + 1

            item_box = tk.Entry(self.frame, width=25)
            item_box.insert(tk.END, item)
            item_box.grid(row=row, column=0)

            price_box = tk.Entry(self.frame, width=5)
            price_box.insert(tk.END, price)
            price_box.grid(row=row, column=1)

            CheckVar = tk.IntVar(value=reduced_tax_rate_flg)
            reduced_tax_rate_flg = ttk.Checkbutton(self.frame, variable=CheckVar)
            reduced_tax_rate_flg.grid(row=row, column=2)

            major_category = ttk.Combobox(self.frame, width=12)
            major_category['values'] = self.major_category_list
            major_category.grid(row=row, column=4)

            medium_category = ttk.Combobox(self.frame, width=12)
            medium_category['values'] = self.medium_category_list
            medium_category.grid(row=row, column=5)

            extra_cost = tk.Entry(self.frame, width=5)
            extra_cost.insert(tk.END, '')
            extra_cost.grid(row=row, column=6)

            extra_cost_detail = tk.Entry(self.frame, width=7)
            extra_cost_detail.insert(tk.END, '')
            extra_cost_detail.grid(row=row, column=7)

            special_cost = ttk.Checkbutton(self.frame)
            special_cost.grid(row=row, column=8)


    def show_item_price_tax_in(self, read_price, read_reduced_tax_rate_flg, tax_excluded):
        price_list = []
        for price in read_price:
            try:
                price = int(price)
            except ValueError:  # 金額を数値として読み取れていない（アルファベット等として認識）場合はいったん0円とする
                price = 0
            price_list.append(price)

        price_tax_in_list = []
        if tax_excluded:
            for row, (price, reduced_tax_rate_flg) in enumerate(zip(price_list, read_reduced_tax_rate_flg)):
                row = row + 1
                tax = self.reduced_tax_rate if reduced_tax_rate_flg else self.tax_rate
                price_tax_in_list.append(int(price * tax))  # 税込にして端数が出た場合は切り捨てとして扱う
        else:
            price_tax_in_list = price_list

        for row, price_tax_in in enumerate(price_tax_in_list):
            row = row + 1
            price_label = tk.Label(self.frame, text=price_tax_in)
            price_label.grid(row=row, column=3)
        
        blank_row_label = tk.Label(self.frame)
        blank_row_label.grid(row=len(read_price)+2,column=3)
        sum_price_str_labal = tk.Label(self.frame, text='税込価格合計')
        sum_price_str_labal.grid(row=len(read_price)+3,column=1, columnspan=2)
        sum_price = sum(price_tax_in_list)
        price_sum_labal = tk.Label(self.frame, text=sum_price)
        price_sum_labal.grid(row=len(read_price)+3,column=3)


def main(read_date, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded, input_file):
    gui = MakeGUI()
    receipt_info_frame = ReceiptInfoFrame(gui.receipt_info_frame, read_date, tax_excluded)
    img_frame = ImgFrame(gui.img_frame, gui.img_width, gui.height, input_file)
    item_frame = ItemFrame(gui.item_frame, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded)
    gui.mainloop()


if __name__ == '__main__':
    main()