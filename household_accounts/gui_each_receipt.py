import re
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image

import config
from calc import calc_price_tax_in, calc_sum_price
from gui_last_page import show_last_page
from ocr import determine_category, read_category
from edit_csv import write_modified_result, write_item_fixes, write_category_fixes
from edit_image import resize_img


class DivideScreen:
    width = config.width
    img_width = 300
    info_width = width - img_width
    height = config.height
    info_height = 60
    operation_height = 100
    item_height = height - info_height - operation_height

    def __init__(self, page):
        self.page = page
        (
            self.img_frame,
            self.receipt_info_frame,
            self.item_frame,
            self.operation_frame,
        ) = self.divide_screen()

    def divide_screen(self):
        receipt_img_frame = tk.Frame(
            self.page, width=self.img_width, height=self.height
        )
        receipt_img_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.S))

        receipt_info_frame = tk.Frame(
            self.page, width=self.info_width, height=self.info_height
        )
        receipt_info_frame.grid(row=0, column=1)

        item_frame = tk.Frame(self.page, width=self.info_width, height=self.item_height)
        item_frame.grid(row=1, column=1)

        operation_frame = tk.Frame(
            self.page, width=self.info_width, height=self.operation_height
        )
        operation_frame.grid(row=2, column=1)

        return receipt_img_frame, receipt_info_frame, item_frame, operation_frame


class ReceiptInfoFrame:
    column_list = ["日付", "店舗", "内税/外税"]
    shop_list = config.shop_list

    def __init__(self, frame, ocr_result):
        self.frame = frame
        self.payment_date = ocr_result["payment_date"]
        self.tax_ex_flg = ocr_result["tax_excluded_flg"]
        self.show_info_column()
        date_place, shop_place, tax_place = self.show_info_value(
            self.payment_date, self.tax_ex_flg
        )
        self.info_places = self.make_places_info(date_place, shop_place, tax_place)

    def show_info_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)

    def show_info_value(self, payment_date, tax_ex_flg):
        def validate_date(value):
            if re.fullmatch(r"[0-9]{4}/[0-9]{2}/[0-9]{2}", value):
                validate_result = True
                date_box["bg"] = "black"
            else:
                validate_result = False
            return validate_result

        def invalid_date():
            date_box["bg"] = "tomato"

        validate_cmd = self.frame.register(validate_date)
        invalid_cmd = self.frame.register(invalid_date)
        date_box = tk.Entry(self.frame)
        date_box.grid(row=1, column=0)
        date_box.insert(tk.END, payment_date)  # バリデーション前に入力して初期値についてもチェックする
        date_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        date_box["validatecommand"] = (validate_cmd, "%s")  # %s : 入力されている値
        date_box["validate"] = "focus"
        date_box["invalidcommand"] = invalid_cmd

        shop_var = ttk.Combobox(self.frame)
        shop_var["values"] = self.shop_list
        shop_var.grid(row=1, column=1)

        tax_var = tk.IntVar()
        tax_var.set(tax_ex_flg)
        tax_in = ttk.Radiobutton(self.frame, text="内税", value=0, variable=tax_var)
        tax_ex = ttk.Radiobutton(self.frame, text="外税", value=1, variable=tax_var)
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


class ImgFrame:
    def __init__(self, frame, width, height, input_file):
        self.width = width
        self.height = height
        self.frame = frame
        self.show_img(input_file)

    def show_img(self, input_file):
        global img
        canvas = tk.Canvas(self.frame, bg="black", width=self.width, height=self.height)
        img = Image.open(input_file)
        resize_input_file = resize_img(input_file, self.width, self.height)

        img = tk.PhotoImage(file=resize_input_file)
        canvas.create_image(self.width / 2, self.height / 2, anchor="center", image=img)
        canvas.pack(expand=True, fill=tk.BOTH)


class ItemFrame:
    column_list = ["必要行", "品目", "読み取り価格", "割引", "軽減税率", "税込価格", "大項目", "中項目"]
    item_names = [
        "item",
        "price",
        "discount",
        "reduced_tax_rate",
        "major_category",
        "medium_category",
        "required",
    ]
    major_category_list = config.major_category_list
    medium_category_list = config.medium_category_list

    def __init__(self, frame, ocr_result, tax_place):
        self.frame = frame
        self.ocr_result = ocr_result
        self.tax_place = tax_place
        self.num_item = len(self.ocr_result["item"])
        self.show_item_column()
        self.item_places = self.insert_ocr_value()
        self.show_button_add_row()
        self.show_price_tax_in()
        self.show_button_recalculation()

    def show_item_column(self):
        for column, text in enumerate(self.column_list):
            date_label = tk.Label(self.frame, text=text)
            date_label.grid(row=0, column=column)

    def place_items(self, row):
        places = {}
        places["required"] = tk.IntVar(value=1)
        required_flg = ttk.Checkbutton(self.frame, variable=places["required"])

        places["item"] = tk.Entry(self.frame, width=25)
        places["price"] = tk.Entry(self.frame, width=6, justify=tk.RIGHT)
        places["discount"] = tk.Entry(self.frame, width=6, justify=tk.RIGHT)

        places["reduced_tax_rate"] = tk.IntVar()
        reduced_tax_rate_flg = ttk.Checkbutton(
            self.frame, variable=places["reduced_tax_rate"]
        )

        places["major_category"] = ttk.Combobox(self.frame, width=12)
        places["major_category"]["values"] = self.major_category_list
        places["medium_category"] = ttk.Combobox(self.frame, width=12)
        places["medium_category"]["values"] = self.medium_category_list

        required_flg.grid(row=row, column=0)
        places["item"].grid(row=row, column=1)
        places["price"].grid(row=row, column=2)
        places["discount"].grid(row=row, column=3)
        reduced_tax_rate_flg.grid(row=row, column=4)
        places["major_category"].grid(
            row=row, column=6
        )  # columnの数値が1つとんでいるのは別関数で税込価格を入れ込むため
        places["medium_category"].grid(row=row, column=7)

        self.validate_item(places)
        self.validate_required(required_flg, places)
        self.validate_price(places["price"])
        return places

    def insert_item_values(self, row, places):
        for column in [
            "item",
            "price",
            "discount",
            "major_category",
            "medium_category",
        ]:
            places[column].insert(tk.END, self.ocr_result[column][row])
        places["reduced_tax_rate"].set(self.ocr_result["reduced_tax_rate_flg"][row])

    def validate_item(self, places):
        def item_validate(value):
            item_read, major_read, medium_read = read_category()
            major_category, medium_category = determine_category(
                value, item_read, major_read, medium_read
            )
            places["major_category"].set("")
            places["major_category"].insert(tk.END, major_category)
            places["medium_category"].set("")
            places["medium_category"].insert(tk.END, medium_category)

        item_validate_cmd = self.frame.register(item_validate)
        places["item"]["validatecommand"] = (item_validate_cmd, "%P")  # %P : 修正後の入力内容
        places["item"]["validate"] = "focusout"

    def validate_required(self, required_flg, places):
        def required_validate():
            if places["required"].get():
                pass
            else:
                places["item"].delete(0, tk.END)
                places["price"].delete(0, tk.END)
                places["discount"].delete(0, tk.END)
                places["major_category"].set("")
                places["medium_category"].set("")
                places["reduced_tax_rate"].set(0)

        required_flg["command"] = required_validate

    def validate_price(self, price_box):
        def price_validate(value):
            try:
                int(value) is int
            except ValueError:
                validate_result = False
            else:
                validate_result = True
                price_box["bg"] = "black"
            return validate_result

        def price_invalid():
            price_box["bg"] = "tomato"

        price_box.focus_set()  # フォーカスした時にバリデーションが走るため、初期値チェックのためにフォーカスする
        price_validate_cmd = self.frame.register(price_validate)
        price_invalid_cmd = self.frame.register(price_invalid)
        price_box["validatecommand"] = (price_validate_cmd, "%s")  # %s : 入力されている値
        price_box["validate"] = "focus"
        price_box["invalidcommand"] = price_invalid_cmd

    def insert_ocr_value(self):
        item_places = {}
        for name in self.item_names:
            item_places[name] = []
        for row in range(self.num_item):
            places = self.place_items(row + 1)
            self.insert_item_values(row, places)
            for name in self.item_names:
                item_places[name].append(places[name])
        return item_places

    def calc_price_tax_in(self):
        def get_value():
            price = list(map(lambda x: x.get(), self.item_places["price"]))
            discount = list(map(lambda x: x.get(), self.item_places["discount"]))
            reduced_tax_rate_flg = list(
                map(lambda x: x.get(), self.item_places["reduced_tax_rate"])
            )
            tax_excluded_flg = self.tax_place.get()
            required_flg = list(map(lambda x: x.get(), self.item_places["required"]))
            return price, discount, reduced_tax_rate_flg, tax_excluded_flg, required_flg

        (
            price,
            discount,
            reduced_tax_rate_flg,
            tax_excluded_flg,
            required_flg,
        ) = get_value()
        price_tax_in_list = calc_price_tax_in(
            price, discount, reduced_tax_rate_flg, tax_excluded_flg
        )
        sum_price = calc_sum_price(price_tax_in_list, required_flg)
        return price_tax_in_list, sum_price

    def show_price_tax_in(self):
        def show_item_prices_tax_in(price_tax_in_list):
            for row, price_tax_in in enumerate(price_tax_in_list):
                row = row + 1
                price_label = tk.Label(self.frame, text=price_tax_in, justify=tk.RIGHT)
                price_label.grid(row=row, column=5, sticky=tk.E, ipadx=20)

        def show_sum_price_tax_in(sum_price):
            blank_row_label = tk.Label(self.frame)
            blank_row_label.grid(row=self.num_item + 1, column=3)

            sum_price_str_labal = tk.Label(self.frame, text="合計額")
            sum_price_str_labal.grid(
                row=self.num_item + 2, column=3, columnspan=2, sticky=tk.E
            )
            price_sum_labal = tk.Label(self.frame, text=sum_price)
            price_sum_labal.grid(row=self.num_item + 2, column=5, sticky=tk.E, ipadx=20)

            self.sum_price_str_labal = sum_price_str_labal
            self.price_sum_labal = price_sum_labal

        price_tax_in_list, sum_price = self.calc_price_tax_in()
        show_item_prices_tax_in(price_tax_in_list)
        show_sum_price_tax_in(sum_price)

    def show_button_recalculation(self):
        def recalc():
            self.show_price_tax_in()

        button_recalculation = ttk.Button(self.frame, text="再計算", command=recalc)
        button_recalculation.grid(
            row=self.num_item + 3,
            column=4,
            rowspan=2,
            columnspan=2,
            sticky=tk.E,
            ipadx=20,
        )
        self.button_recalculation = button_recalculation

    def add_row(self):
        places = self.place_items(self.num_item + 1)
        for name in self.item_names:
            self.item_places[name].append(places[name])
        self.num_item += 1

        self.sum_price_str_labal.destroy()
        self.price_sum_labal.destroy()
        self.show_price_tax_in()

        self.button_recalculation.destroy()
        self.show_button_recalculation()

    def show_button_add_row(self):
        add_row_button = ttk.Button(self.frame, text="行を増やす", command=self.add_row)
        add_row_button.grid(
            row=self.num_item + 8,  # 最大8行追加できる
            column=1,
            rowspan=1,
            columnspan=1,
            sticky=tk.E,
            ipadx=20,
        )


class OperationFrame:
    def __init__(self, frame, info_places, item_places, gui, input_file, ocr_result):
        self.frame = frame
        self.gui = gui
        self.ocr_result = ocr_result
        self.info_places = info_places
        self.item_places = item_places
        self.receipt_no = gui.input_path_list.index(input_file)
        self.num_receipts = len(gui.input_path_list)
        self.show_button_next_receipt()

    def next_receipt(self):
        self.gui.change_page()
        next_receipt_no = self.receipt_no + 1
        next_input_file = self.gui.input_path_list[next_receipt_no]
        next_ocr_result = self.gui.ocr_results[next_input_file]
        main(next_ocr_result, next_input_file, self.gui.next_page, self.gui)

    def show_button_next_receipt(self):
        def next_step():
            write_modified_result(self.info_places, self.item_places)
            write_item_fixes(self.ocr_result["item"], self.item_places["item"])
            write_category_fixes(
                self.item_places["item"],
                self.item_places["major_category"],
                self.item_places["medium_category"],
            )
            if self.receipt_no + 1 < self.num_receipts:
                self.next_receipt()
            else:
                show_last_page(self.gui)

        button_text = "次のレシートへ →" if self.receipt_no + 1 < self.num_receipts else "修正完了"
        change_page_button = tk.Button(self.frame, text=button_text, command=next_step)
        change_page_button.pack(ipadx=100, ipady=15)


def main(ocr_result, input_file, page, gui):
    page = DivideScreen(page)
    receipt_info_frame = ReceiptInfoFrame(page.receipt_info_frame, ocr_result)
    info_places = receipt_info_frame.info_places
    ImgFrame(page.img_frame, page.img_width, page.height, input_file)
    item_frame = ItemFrame(page.item_frame, ocr_result, info_places["tax"])
    item_places = item_frame.item_places
    OperationFrame(
        page.operation_frame, info_places, item_places, gui, input_file, ocr_result
    )


if __name__ == "__main__":
    main()
