import csv
import os
import pyocr
import pyocr.builders
import re
import time
from datetime import datetime
from PIL import Image

from get_file_path_list import get_input_path_list


class OcrReceipt:
    date_regex = r'.{4}(/|年).{1,2}(/|月)[0-9]{1,2}'
    total_regex = r'(合計|小計|ノヽ言十|消費税).*[0-9]*'
    item_price_regex = r'([0-9]|\*|＊|※|[a-z]|[A-Z])\Z'  # 末尾が数字か軽減税率の記号かアルファベット（数字が読み取れていない場合用）
    reduced_tax_regex = r'(\*|＊|※|W|w)'
    top_num_regex = r'^[0-9]*'
    tax_ex_regex = r'外税'
    tax_in_regex = r'(内税|内消費税等)'
    conversion_num_before = ['O', 'U', 'b', 'Z', '<', 'i']  # アルファベットとして認識されている価格を変換するため
    conversion_num_after = ['0', '0', '6', '2', '2', '1']
    separator = r'区切位置'
    discount_regex = r'(割り*引|値引)'


    def __init__(self, input_file):
        content_en, content = self.ocr(input_file)
        self.payment_date = self.get_payment_date(content)
        self.tax_excluded = self.get_tax_excluded_included(content)
        main_contents = self.get_main_contents(content, content_en)
        self.reduced_tax_rate_flg = self.get_reduced_tax_rate_flg(main_contents)
        self.item, price = self.separate_item_and_price(main_contents)
        self.price = self.modify_price(price)
        self.discount = self.extract_discount()
        self.exclude_unnecessary_row()


    def ocr(self, input_file):
        tool = pyocr.get_available_tools()[0]
        receipt_ocr = tool.image_to_string(
            Image.open(input_file),
            lang='jpn',
            builder=pyocr.builders.LineBoxBuilder(tesseract_layout=4)
            )
        
        receipt_content = list(map(lambda x: x.content, receipt_ocr))
        receipt_content = [i for i in receipt_content if i != '']
        content_en = []
        content = []
        for row in receipt_content:
            index_separator = row.rfind(' ')  # 最も右のスペースを品目名と価格の区切りとみなす
            row_en = row[:index_separator] + self.separator + row[index_separator+1:]
            row_en = re.sub(r' ', r'', row_en)
            row = re.sub(r' ', r'', row)
            content_en.append(row_en)
            content.append(row)
        return content_en, content


    def get_payment_date(self, content):
        payment_date = [re.search(self.date_regex, s).group() for s in content if re.search(self.date_regex+r'(\(|日)', s)]
        payment_date = payment_date[0] if payment_date != [] else '2000/01/01'
        payment_date = re.sub(r'(年|月)', r'/', payment_date)
        payment_date = datetime.strptime(payment_date, '%Y/%m/%d').strftime('%Y/%m/%d')
        return payment_date


    def get_tax_excluded_included(self, content):
        tax_excluded_flg = [1 for s in content if re.search(self.tax_ex_regex,s)]
        tax_included_flg = [1 for s in content if re.search(self.tax_in_regex,s)]
        tax_excluded = 1 if len(tax_excluded_flg)>len(tax_included_flg) else 0  # 外税判断の文字列が内税判断の文字列を超えた数存在すれば外税とする
        return tax_excluded


    def get_main_contents(self, content, content_en):
        try:
            start_low = [content.index(s) for s in content if re.search(self.date_regex, s)][0] + 1  # payment_dateの次の行が開始行とする
        except IndexError:
            start_low = 0  # payment_dateがない場合は最初の行を開始行とする
        sum_lows = [content.index(s) for s in content if re.search(self.total_regex, s)]
        end_low = sum_lows[0] if sum_lows != [] else len(content)-1  # 合計行とみなす列があればその上の列を終了行とし、なければ最後まで含める
        main_contents = content_en[start_low:end_low]
        main_contents = [s for s in main_contents if re.search(self.item_price_regex, s)]  
        return main_contents


    def get_reduced_tax_rate_flg(self, main_contents):
        reduced_tax_rate_flg = [1 if re.search(self.reduced_tax_regex, s) else 0 for s in main_contents]
        return reduced_tax_rate_flg


    def separate_item_and_price(self, main_contents):
        item_and_price = [re.sub(self.reduced_tax_regex, r'', s) for s in main_contents]  # 軽減税率の記号は取り除く
        item = [s[:s.find(self.separator)] for s in item_and_price]  # separatorより左が品目名
        item = [re.sub(self.top_num_regex, r'', s) for s in item]
        price = [s[s.find(self.separator)+len(self.separator):] for s in item_and_price]  # separatorより右が価格
        return item, price
    

    def extract_discount(self):
        discount = [0] * len(self.item)
        index_discount = [self.item.index(s) for s in self.item if re.search(self.discount_regex, s)]
        if len(index_discount) > 0:
            for i in index_discount:
                discount[i-1] = self.price[i]
            for i in sorted(index_discount, reverse=True):  # indexがずれるので上のforループと分けている
                del self.price[i]
                del self.item[i]
                del self.reduced_tax_rate_flg[i]
                del discount[i]
        return discount


    def modify_price(self, price):
        price = [re.sub(r'(\\|:)', r'', s) for s in price]
        for before, after in zip(self.conversion_num_before, self.conversion_num_after):
            price = [re.sub(before, after, p) for p in price]
        price = [re.sub(r'([A-Z]|[a-z])', r'', p) for p in price]
        return price
    

    def exclude_unnecessary_row(self):
        index_not_price = [i for i, p in enumerate(self.price) if p[0]=='0']  # 価格が0から始まっている
        index_high_price = [i for i, p in enumerate(self.price) if int(p)>1000000]  # 10万円以上
        index_empty_item = [i for i, p in enumerate(self.item) if p=='']  # 品目名がない
        index_unnecessary = set(index_not_price + index_high_price + index_empty_item)
        if len(index_unnecessary) > 0:
            for index in sorted(index_unnecessary, reverse=True):
                del self.price[index]
                del self.item[index]
                del self.reduced_tax_rate_flg[index]
                del self.discount[index]


def translate_item_fixes(item_list):
    csv_path = os.path.join(os.path.dirname(__file__), '../csv/learning_file/item_ocr_fix.csv')
    with open(csv_path, mode='r') as file:
        reader = [row for row in csv.reader(file)]
        before = [s[0] for s in reader]
        after = [s[1] for s in reader]
    item_fix = [after[before.index(s)] if s in before else s for s in item_list]
    return item_fix


def read_category():
    csv_path = os.path.join(os.path.dirname(__file__), '../csv/learning_file/category_fix.csv')
    with open(csv_path, mode='r') as file:
        reader = [row for row in csv.reader(file)]
        item_read = [s[0] for s in reader]
        major_read = [s[1] for s in reader]
        medium_read = [s[2] for s in reader]
    return item_read, major_read, medium_read


def determine_category(item, item_read, major_read, medium_read):
    major_category = major_read[item_read.index(item)] if item in item_read else ''
    medium_category = medium_read[item_read.index(item)] if item in item_read else ''
    return major_category, medium_category


def group_category(item):
    item_read, major_read, medium_read = read_category()
    category = [(determine_category(s, item_read, major_read, medium_read)) for s in item]
    major_category = [s[0] for s in category]
    medium_category = [s[1] for s in category]
    return major_category, medium_category


def summing_up_ocr_results(ocr, item_fix, major_category, medium_category):
    result = {}
    result['payment_date'] = ocr.payment_date
    result['item'] = item_fix
    result['price'] = ocr.price
    result['reduced_tax_rate_flg'] = ocr.reduced_tax_rate_flg
    result['tax_excluded_flg'] = ocr.tax_excluded
    result['discount'] = ocr.discount
    result['major_category'] = major_category
    result['medium_category'] = medium_category
    return result


def indicate_processing_status(no, num):
    process_per = round(no / num * 100, 0)
    process_bar = ('=' * no) + (' ' * (num - no))
    print('\r処理状況: [{}] {}%'.format(process_bar, process_per), end='')
    time.sleep(0.1)


def main():
    input_path_list = get_input_path_list('../img/interim/each_receipt', 'png')
    ocr_results = {}
    for i, input_file in enumerate(input_path_list):
        ocr = OcrReceipt(input_file)
        item_fix = translate_item_fixes(ocr.item)
        major_category, medium_category = group_category(item_fix)
        ocr_results[input_file] = summing_up_ocr_results(ocr, item_fix, major_category, medium_category)
        indicate_processing_status(i, len(input_path_list))
    return ocr_results

if __name__ == '__main__':
    main()