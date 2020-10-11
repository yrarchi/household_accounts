import datetime
import csv
import os
import re
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image

import config
from calc import calc_price_tax_in, calc_sum_price
from gui_last_page import show_last_page
from resize_image import resize_img


class DivideScreen():
    width = config.width
    img_width = 300
    info_width = width - img_width
    height = config.height
    info_height = 60
    operation_height = 100
    item_height = height - info_height - operation_height

    def __init__(self, page):
        self.page = page
        self.img_frame, self.receipt_info_frame, self.item_frame, self.operation_frame = self.divide_screen()


    def divide_screen(self):
        receipt_img_frame = tk.Frame(self.page, width=self.img_width, height=self.height)
        receipt_img_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.S))

        receipt_info_frame = tk.Frame(self.page, width=self.info_width, height=self.info_height)
        receipt_info_frame.grid(row=0, column=1)

        item_frame = tk.Frame(self.page, width=self.info_width, height=self.item_height)
        item_frame.grid(row=1, column=1)

        operation_frame = tk.Frame(self.page, width=self.info_width, height=self.operation_height)
        operation_frame.grid(row=2, column=1)

        return receipt_img_frame, receipt_info_frame, item_frame, operation_frame


class ReceiptInfoFrame():
    column_list = ['日付', '店舗', '内税/外税']
    shop_list = config.shop_list

    def __init__(self, frame, read_date, tax_excluded):
        self.frame = frame
        self.show_info_column()
        date_place, shop_place, tax_place = self.show_info_value(read_date, tax_excluded)
        self.info_places = self.make_places_info(date_place, shop_place, tax_place)


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


        validate_cmd = self.frame.register(validate_date)
        invalid_cmd = self.frame.register(invalid_date)
        date_box = tk.Entry(self.frame)
        date_box.grid(row=1, column=0)
        date_box.insert(tk.END, read_date)  # バリデーション前に入力して初期値についてもチェックする
        date_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        date_box['validatecommand'] = (validate_cmd, '%s')  # %s : 入力されている値
        date_box['validate'] = 'focus'
        date_box['invalidcommand'] = (invalid_cmd)

        shop_var = ttk.Combobox(self.frame)
        shop_var['values'] = self.shop_list
        shop_var.grid(row=1, column=1)

        tax_var = tk.IntVar()
        tax_var.set(tax_excluded)
        tax_in = ttk.Radiobutton(self.frame, text='内税', value=0, variable=tax_var)
        tax_ex = ttk.Radiobutton(self.frame, text='外税', value=1, variable=tax_var)
        tax_in.grid(row=1, column=2)
        tax_ex.grid(row=1, column=3)

        return date_box, shop_var, tax_var


    def make_places_info(self, date_place, shop_place, tax_place):
        info_places = {}
        name_list = ["date", "shop", "tax"]
        place_list = [date_place, shop_place, tax_place]
        for name, place in zip(name_list, place_list):
            info_places[name] = place
        return info_places


class ImgFrame():
    def __init__(self, frame, width, height, input_file):
        self.width = width
        self.height = height
        self.frame = frame
        self.show_img(input_file)


    def show_img(self, input_file):
        global img
        canvas = tk.Canvas(self.frame, bg='black', width = self.width, height = self.height)
        img = Image.open(input_file)
        resize_input_file = resize_img(input_file, self.width, self.height)

        img = tk.PhotoImage(file = resize_input_file)
        canvas.create_image(self.width/2, self.height/2, anchor='center', image=img)
        canvas.pack(expand = True, fill = tk.BOTH)


class ItemFrame():
    column_list = ['品目', '読み取り価格', '軽減税率', '税込価格', '大項目', '中項目', '付帯費', '付帯費内容', '特別費', '必要行']
    major_category_list = config.major_category_list
    medium_category_list = config.medium_category_list
        
    def __init__(self, frame, read_item, read_price, read_reduced_tax_rate_flg, read_tax_excluded, tax_place):
        self.num_item = len(read_price)
        self.frame = frame
        self.show_item_column()
        self.item_places = self.get_place_items(read_item, read_price, read_reduced_tax_rate_flg)
        self.show_price_tax_in(read_price, read_reduced_tax_rate_flg, read_tax_excluded)
        self.show_button_recalculation(self.item_places, tax_place)


    def show_item_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)


    def show_item_value(self, item, price, reduced_tax_rate_flg, row):
        def price_validate(value):
            try:
                int(value) is int
            except ValueError:
                validate_result = False
            else:
                validate_result = True
                price_box['bg'] = 'black'
            return validate_result


        def price_invalid():
            price_box['bg'] = 'tomato'


        def required_validate():
            if required_flg_var.get():
                pass
            else:
                item_box.delete(0, tk.END)
                price_box.delete(0, tk.END)
                major_category.set('')
                medium_category.set('')
                extra_cost.delete(0, tk.END)
                extra_cost_detail.delete(0, tk.END)

        row = row + 1

        item_box = tk.Entry(self.frame, width=25)
        item_box.insert(tk.END, item)
        item_box.grid(row=row, column=0)

        price_validate_cmd = self.frame.register(price_validate)
        price_invalid_cmd = self.frame.register(price_invalid)
        price_box = tk.Entry(self.frame, width=5, justify=tk.RIGHT)
        price_box.grid(row=row, column=1)
        price_box.insert(tk.END, price)  # バリデーション前に入力して初期値についてもチェックする
        price_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        price_box['validatecommand'] = (price_validate_cmd, '%s')  # %s : 入力されている値
        price_box['validate'] = 'focus'
        price_box['invalidcommand'] = (price_invalid_cmd)

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

        required_flg_var = tk.IntVar(value=1)
        required_flg = ttk.Checkbutton(self.frame, variable=required_flg_var, command=required_validate)
        required_flg.grid(row=row, column=9)

        return item_box, price_box, reduced_tax_rate_flg_var, major_category, medium_category, required_flg_var


    def get_place_items(self, item_list, price_list, reduced_tax_rate_flg_list):
        item_places = {}
        item_places["item"] = []
        item_places["price"] = []
        item_places["reduced_tax_rate"] = []
        item_places["major_category"] = []
        item_places["medium_category"] = []
        item_places["required"] = []
        for row, (item, price, reduced_tax_rate_flg) in enumerate(zip(item_list, price_list, reduced_tax_rate_flg_list)):
            item_box, price_box, reduced_tax_rate_flg_var, major_category, medium_category, required_flg_var \
                = self.show_item_value(item, price, reduced_tax_rate_flg, row)
            item_places["item"].append(item_box)
            item_places["price"].append(price_box)
            item_places["reduced_tax_rate"].append(reduced_tax_rate_flg_var)
            item_places["major_category"].append(major_category)
            item_places["medium_category"].append(medium_category)
            item_places["required"].append(required_flg_var)
        return item_places


    def show_price_tax_in(self, price_list, reduced_tax_rate_flg_list, tax_excluded_list):        
        def show_item_prices_tax_in(price_tax_in_list):
            for row, price_tax_in in enumerate(price_tax_in_list):
                row = row + 1
                price_label = tk.Label(self.frame, text=price_tax_in, justify=tk.RIGHT)
                price_label.grid(row=row, column=3, sticky=tk.E, ipadx=20)
            

        def show_sum_price_tax_in(sum_price):
            blank_row_label = tk.Label(self.frame)
            blank_row_label.grid(row=self.num_item+2,column=3)

            sum_price_str_labal = tk.Label(self.frame, text='税込価格合計')
            sum_price_str_labal.grid(row=self.num_item+3,column=1, columnspan=2, sticky=tk.E)
            
            price_sum_labal = tk.Label(self.frame, text=sum_price)
            price_sum_labal.grid(row=self.num_item+3,column=3, sticky=tk.E, ipadx=20)


        price_tax_in_list = calc_price_tax_in(price_list, tax_excluded_list, reduced_tax_rate_flg_list)
        sum_price = calc_sum_price(price_tax_in_list, self.item_places["required"])
        show_item_prices_tax_in(price_tax_in_list)
        show_sum_price_tax_in(sum_price)


    def show_button_recalculation(self, item_places, tax_place):
        def recalc():
            price = list(map(lambda x: x.get(), item_places["price"]))
            reduced_tax_rate_flg = list(map(lambda x: x.get(), item_places["reduced_tax_rate"]))
            tax_excluded = tax_place.get()
            self.show_price_tax_in(price, reduced_tax_rate_flg, tax_excluded)
        
        calc_button = ttk.Button(self.frame, text='再計算', command=recalc)
        calc_button.grid(row=self.num_item+4, column=3, sticky=tk.E)


class OperationFrame():
    def __init__(self, frame, info_place, item_places, gui, input_file):
        self.frame = frame
        self.date_place = info_place["date"]
        self.shop_place = info_place["shop"]
        self.item_place = item_places["item"]
        self.price_place = item_places["price"]
        self.major_category_place = item_places["major_category"]
        self.medium_category_place = item_places["medium_category"]
        self.required_place = item_places["required"]
        self.show_button_next_receipt(gui, input_file)


    def show_button_next_receipt(self, gui, input_file):
        def next_step():
            def write_modified_result():
                date = self.date_place.get()
                shop = self.shop_place.get()
                today = datetime.datetime.now().strftime('%Y%m%d')
                csv_path = os.path.join(os.path.dirname(__file__), '../csv/{}.csv'.format(today))
                with open(csv_path, mode='a') as file:
                    for item, price, major_category, medium_category, required \
                         in zip(self.item_place, self.price_place, self.major_category_place, self.medium_category_place, self.required_place):
                        if required.get() == 1:
                            row = [date, item.get(), price.get(), major_category.get(), medium_category.get(), shop] 
                            csv.writer(file).writerow(row)
            

            def next_receipt():
                gui.change_page()
                next_receipt_no = receipt_no + 1
                next_input_file = gui.input_path_list[next_receipt_no]
                next_ocr_result = gui.ocr_results[next_input_file]
                main(next_ocr_result, next_input_file, gui.next_page, gui)

                
            write_modified_result()
            if receipt_no + 1 < num_receipts:
                next_receipt()
            else:
                show_last_page(gui)

        receipt_no = gui.input_path_list.index(input_file)
        num_receipts = len(gui.input_path_list)
        button_text = '次のレシートへ →' if receipt_no + 1 < num_receipts else '修正完了'
        change_page_button = tk.Button(self.frame, text=button_text, command=next_step)
        change_page_button.pack(ipadx=100, ipady=15)


def main(ocr_result, input_file, page, gui):
    read_date, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded = [i for i in ocr_result]
    page = DivideScreen(page)
    receipt_info_frame = ReceiptInfoFrame(page.receipt_info_frame, read_date, tax_excluded)
    info_places = receipt_info_frame.info_places
    img_frame = ImgFrame(page.img_frame, page.img_width, page.height, input_file)
    item_frame = ItemFrame(page.item_frame, read_item, read_price, read_reduced_tax_rate_flg, tax_excluded, info_places["tax"])
    item_places = item_frame.item_places
    operation_frame = OperationFrame(page.operation_frame, info_places, item_places, gui, input_file)


if __name__ == '__main__':
    main()