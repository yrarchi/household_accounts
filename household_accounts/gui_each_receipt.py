import datetime
import csv
import re
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image
from resize_image import resize_img
from gui_make_pages import MakePages


class DivideScreen():
    width = 1400
    img_width = 300
    info_width = width - img_width
    height = 600
    info_height = 60
    operation_height = 100
    item_height = height - info_height - operation_height

    def __init__(self, page2):
        self.page2 = page2
        self.img_frame, self.receipt_info_frame, self.item_frame, self.operation_frame = self.divide_screen()


    def divide_screen(self):
        receipt_img_frame = tk.Frame(self.page2, width=self.img_width, height=self.height)
        receipt_img_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.S))

        receipt_info_frame = tk.Frame(self.page2, width=self.info_width, height=self.info_height)
        receipt_info_frame.grid(row=0, column=1)

        item_frame = tk.Frame(self.page2, width=self.info_width, height=self.item_height)
        item_frame.grid(row=1, column=1)

        operation_frame = tk.Frame(self.page2, width=self.info_width, height=self.operation_height)
        operation_frame.grid(row=2, column=1)

        return receipt_img_frame, receipt_info_frame, item_frame, operation_frame


class ReceiptInfoFrame():
    column_list = ['日付', '店舗', '内税/外税']
    shop_list = ['店舗', 'コンビニ']  # あとでDBから引っ張るようにする

    def __init__(self, frame, read_date, tax_excluded, page2, gui):
        self.frame = frame
        self.page2 = page2
        self.gui = gui
        self.show_info_column()
        self.date_box, self.shop, self.tax_var = self.show_info_value(read_date, tax_excluded)


    def show_info_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)


    def show_info_value(self, read_date, tax_excluded):
        def validate_date(value):
            if re.fullmatch(r'[0-9]{4}/[0-9]{2}/[0-9]{2}', value):
                validate_result = True
                date_box['bg'] = 'black'
            else:
                validate_result = False
            return validate_result


        def invalid_date():
            date_box['bg'] = 'tomato'


        validate_cmd = self.gui.register(validate_date)
        invalid_cmd = self.gui.register(invalid_date)
        date_box = tk.Entry(self.frame)
        date_box.grid(row=1, column=0)
        date_box.insert(tk.END, read_date)  # バリデーション前に入力して初期値についてもチェックする
        date_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        date_box['validatecommand'] = (validate_cmd, '%s')  # %s : 入力されている値
        date_box['validate'] = 'focus'
        date_box['invalidcommand'] = (invalid_cmd)


        shop = ttk.Combobox(self.frame)
        shop['values'] = self.shop_list
        shop.grid(row=1, column=1)

        tax_var = tk.IntVar()
        tax_var.set(tax_excluded)
        tax_in = ttk.Radiobutton(self.frame, text='内税', value=0, variable=tax_var)
        tax_ex = ttk.Radiobutton(self.frame, text='外税', value=1, variable=tax_var)
        tax_in.grid(row=1, column=2)
        tax_ex.grid(row=1, column=3)

        return date_box, shop, tax_var


class ImgFrame():
    def __init__(self, frame, width, height, input_file):
        self.width = width
        self.height = height
        self.show_img(frame, input_file)


    def show_img(self, frame, input_file):
        global img
        canvas = tk.Canvas(frame, bg='black', width = self.width, height = self.height)
        img = Image.open(input_file)
        resize_input_file = resize_img(input_file, self.width, self.height)

        img = tk.PhotoImage(file = resize_input_file)
        canvas.create_image(0, 0, anchor='nw', image=img)
        canvas.pack(expand = True, fill = tk.BOTH)


class ItemFrame():
    major_category_list = ['食費', '光熱費']  # todo: DBから引っ張るようにする
    medium_category_list = ['野菜', '米']  # todo: DBから引っ張るようにする
    column_list = ['品目', '読み取り価格', '軽減税率', '税込価格', '大項目', '中項目', '付帯費', '付帯費内容', '特別費']
    tax_rate = 1.1
    reduced_tax_rate = 1.08

        
    def __init__(self, frame, read_item, read_price, read_reduced_tax_rate_flg, read_tax_excluded, tax_place, page2, gui):
        self.num_item = len(read_price)
        self.frame = frame
        self.page2 = page2
        self.gui = gui
        self.show_item_column()
        self.item_place, self.price_place, self.reduced_tax_rate_place, self.major_category_place, self.medium_category_place \
            = self.get_item_value_list(read_item, read_price, read_reduced_tax_rate_flg)
        self.show_price_tax_in(read_price, read_reduced_tax_rate_flg, read_tax_excluded)
        self.show_button_recalculation(self.price_place, self.reduced_tax_rate_place, tax_place)


    def show_item_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)


    def show_item_value(self, item, price, reduced_tax_rate_flg, row):
        def validate_price(value):
            try:
                int(value) is int
            except ValueError:
                validate_result = False
            else:
                validate_result = True
                price_box['bg'] = 'black'
            return validate_result


        def invalid_price():
            price_box['bg'] = 'tomato'


        row = row + 1

        item_box = tk.Entry(self.frame, width=25)
        item_box.insert(tk.END, item)
        item_box.grid(row=row, column=0)

        validate_cmd = self.gui.register(validate_price)
        invalid_cmd = self.gui.register(invalid_price)
        price_box = tk.Entry(self.frame, width=5, justify=tk.RIGHT)
        price_box.grid(row=row, column=1)
        price_box.insert(tk.END, price)  # バリデーション前に入力して初期値についてもチェックする
        price_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        price_box['validatecommand'] = (validate_cmd, '%s')  # %s : 入力されている値
        price_box['validate'] = 'focus'
        price_box['invalidcommand'] = (invalid_cmd)
        

        reduced_tax_rate_flg_var = tk.IntVar(value=reduced_tax_rate_flg)
        reduced_tax_rate_flg = ttk.Checkbutton(self.frame, variable=reduced_tax_rate_flg_var)
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

        return item_box, price_box, reduced_tax_rate_flg_var, major_category, medium_category


    def get_item_value_list(self, item_list, price_list, reduced_tax_rate_flg_list):
        item_place = []
        price_place = []
        reduced_tax_rate_place = []
        major_category_place = []
        medium_category_place = []
        for row, (item, price, reduced_tax_rate_flg) in enumerate(zip(item_list, price_list, reduced_tax_rate_flg_list)):
            item_box, price_box, reduced_tax_rate_flg_var, major_category, medium_category \
                = self.show_item_value(item, price, reduced_tax_rate_flg, row)
            item_place.append(item_box)
            price_place.append(price_box)
            reduced_tax_rate_place.append(reduced_tax_rate_flg_var)
            major_category_place.append(major_category)
            medium_category_place.append(medium_category)
        return item_place, price_place, reduced_tax_rate_place, major_category_place, medium_category_place


    def show_price_tax_in(self, price_list, reduced_tax_rate_flg_list, tax_excluded_list):
        def calc_price_tax_in():
            trans_price_list = []
            for price in price_list:
                try:
                    price = int(price)
                except ValueError:  # 金額を数値として読み取れていない（アルファベット等として認識）場合はいったん0円とする
                    price = 0
                trans_price_list.append(price)

            price_tax_in_list = []
            if tax_excluded_list:
                for row, (price, reduced_tax_rate_flg) in enumerate(zip(trans_price_list, reduced_tax_rate_flg_list)):
                    row = row + 1
                    tax = self.reduced_tax_rate if reduced_tax_rate_flg else self.tax_rate
                    price_tax_in_list.append(int(price * tax))  # 税込にして端数が出た場合は切り捨てとして扱う
            else:
                price_tax_in_list = trans_price_list
            return price_tax_in_list

        
        def show_item_prices_tax_in(price_tax_in_list):
            for row, price_tax_in in enumerate(price_tax_in_list):
                row = row + 1
                price_label = tk.Label(self.frame, text=price_tax_in, justify=tk.RIGHT)
                price_label.grid(row=row, column=3, sticky=tk.E, ipadx=20)
            

        def show_sum_price_tax_in(price_tax_in_list):
            blank_row_label = tk.Label(self.frame)
            blank_row_label.grid(row=self.num_item+2,column=3)

            sum_price_str_labal = tk.Label(self.frame, text='税込価格合計')
            sum_price_str_labal.grid(row=self.num_item+3,column=1, columnspan=2, sticky=tk.E)
            
            sum_price = sum(price_tax_in_list)
            price_sum_labal = tk.Label(self.frame, text=sum_price)
            price_sum_labal.grid(row=self.num_item+3,column=3, sticky=tk.E, ipadx=20)


        price_tax_in_list = calc_price_tax_in()
        show_item_prices_tax_in(price_tax_in_list)
        show_sum_price_tax_in(price_tax_in_list)


    def show_button_recalculation(self, price_place, reduced_tax_rate_place, tax_place):
        def recalc():
            price = list(map(lambda x: x.get(), price_place))
            reduced_tax_rate_flg = list(map(lambda x: x.get(), reduced_tax_rate_place))
            tax_excluded = tax_place.get()
            self.show_price_tax_in(price, reduced_tax_rate_flg, tax_excluded)
        
        calc_button = ttk.Button(self.frame, text='再計算', command=recalc)
        calc_button.grid(row=self.num_item+4, column=3, sticky=tk.E)


class OperationFrame():
    def __init__(self, frame, date_place, shop_place, item_place, price_place, major_category_place, medium_category_place, gui, input_file):
        self.frame = frame
        self.date_place = date_place
        self.shop_place = shop_place
        self.item_place = item_place
        self.price_place = price_place
        self.major_category_place = major_category_place
        self.medium_category_place = medium_category_place
        self.show_button_write_csv()
        self.show_button_change_page(gui, input_file)


    def show_button_write_csv(self):
        def write_csv():
            date = self.date_place.get()
            shop = self.shop_place.get()
            today = datetime.datetime.now().strftime('%Y%m%d')
            with open('./csv/{}.csv'.format(today), mode='a') as file:
                for item, price, major_category, medium_category in zip(self.item_place, self.price_place, self.major_category_place, self.medium_category_place):
                    row = [date, item.get(), price.get(), major_category.get(), medium_category.get(), shop]
                    csv.writer(file).writerow(row)
        
        write_csv_button = ttk.Button(self.frame, text='csvファイルに書き込み', command=write_csv)
        write_csv_button.grid(row=0, column=0)


    def show_button_change_page(self, gui, input_file):
        change_page_button = tk.Button(self.frame, text="次のレシートへ → ", command=lambda : MakePages.next_receipt(gui, input_file))
        change_page_button.grid(row=0, column=1)


def main(ocr_result, input_file, page2, gui):
    read_date, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded = [i for i in ocr_result]
    page2 = DivideScreen(page2)
    receipt_info_frame = ReceiptInfoFrame(page2.receipt_info_frame, read_date, tax_excluded, page2, gui)
    date_place, shop_place, tax_place = receipt_info_frame.date_box, receipt_info_frame.shop, receipt_info_frame.tax_var
    img_frame = ImgFrame(page2.img_frame, page2.img_width, page2.height, input_file)
    item_frame = ItemFrame(page2.item_frame, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded, tax_place, page2, gui)

    item_place, price_place, reduced_tax_rate_place, major_category_place, medium_category_place \
        = item_frame.item_place, item_frame.price_place, item_frame.reduced_tax_rate_place, item_frame.major_category_place, item_frame.medium_category_place
    operation_frame = OperationFrame(page2.operation_frame, date_place, shop_place, item_place, price_place, major_category_place, medium_category_place, gui, input_file)


if __name__ == '__main__':
    main()