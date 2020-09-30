import os
from PIL import Image
import pyocr
import pyocr.builders
import re
from get_file_path_list import get_input_path_list


class OcrReceipt:
    date_regex = r'.{4}(/|年).{1,2}(/|月)[0-9]{1,2}'
    total_regex = r'(合計|小計|ノヽ言十|消費税).*[0-9]*'
    item_price_regex = r'([0-9]|\*|＊|※|[a-z]|[A-Z])\Z'  # 末尾が数字か軽減税率の記号かアルファベット（数字が読み取れていない場合用）
    price_regex = r'([0-9]|[a-z]|[A-Z])*\Z'  # アルファベットは数値が誤って変換されていることがあるため
    reduced_tax_regex = r'(\*|＊|※)'
    top_num_regex = r'^[0-9]*'
    tax_ex_regex = r'外税'
    tax_in_regex = r'(内税|内消費税等)'

    def ocr(self, input_file):
        tool = pyocr.get_available_tools()[0]
        receipt_ocr = tool.image_to_string(
            Image.open(input_file),
            lang='jpn',
            builder=pyocr.builders.LineBoxBuilder(tesseract_layout=4)
            )
        receipt_content = []
        for i in range(len(receipt_ocr)):
            content = receipt_ocr[i].content
            content = re.sub(r' ', r'', content)
            if content != '':
                receipt_content.append(content)
        return receipt_content


    def get_payment_date(self, receipt_content):
        payment_date = 0
        payment_date = [re.search(self.date_regex, s).group() for s in receipt_content if re.search(self.date_regex+r'(\(|日)', s)]
        payment_date = re.sub(r'(年|月)', r'/', payment_date[0])
        return payment_date


    def get_item_price_reduced_tax_rate_flg(self, receipt_content):
        start_low = [receipt_content.index(s) for s in receipt_content if re.search(self.date_regex, s)][0] + 1  # payment_dateの次の行が開始行とする
        end_low = [receipt_content.index(s) for s in receipt_content if re.search(self.total_regex, s)][0]

        item_and_price = receipt_content[start_low:end_low]
        item_and_price = [s for s in item_and_price if re.search(self.item_price_regex, s)]  

        reduced_tax_rate_flg = [1 if re.search(self.reduced_tax_regex, s) else 0 for s in item_and_price]
        item_and_price = [re.sub(self.reduced_tax_regex, r'', s) for s in item_and_price]  # 軽減税率の判定終わったらその記号は取り除く

        item = [re.sub(self.price_regex, r'', s) for s in item_and_price]
        item = [re.sub(self.top_num_regex, r'', s) for s in item]
        item = [re.sub(r'\\', r'', s) for s in item]
        price = [re.search(self.price_regex, s).group() for s in item_and_price]
        return item, price, reduced_tax_rate_flg


    def get_tax_excluded_included(self, receipt_content):
        tax_excluded_flg = [1 for s in receipt_content if re.search(self.tax_ex_regex,s)]
        tax_included_flg = [1 for s in receipt_content if re.search(self.tax_in_regex,s)]
        tax_excluded = 1 if len(tax_excluded_flg)>len(tax_included_flg) else 0  # 外税判断の文字列が内税判断の文字列を超えた数存在すれば外税とする
        return tax_excluded


def main():
    input_path_list = get_input_path_list(relative_path='../img/interim', extension='png')
    input_file = input_path_list[0]

    ocr = OcrReceipt()
    receipt_content = ocr.ocr(input_file)
    payment_date = ocr.get_payment_date(receipt_content)
    item, price, reduced_tax_rate_flg = ocr.get_item_price_reduced_tax_rate_flg(receipt_content)
    tax_excluded = ocr.get_tax_excluded_included(receipt_content)
    return payment_date, item, price, reduced_tax_rate_flg, tax_excluded, input_file


if __name__ == '__main__':
    main()