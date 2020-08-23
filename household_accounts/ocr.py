import os
from PIL import Image
import pyocr
import pyocr.builders
import re


def get_input_file_list():
    path = './img/unprocessed'
    files = os.listdir(path)
    input_file_list = [os.path.join(path, f) for f in files if re.search(r'.+\.JPG', f)]
    return input_file_list


class OcrReceipt:
    date_regex = r'.{4}(/|年).+(/|月)[0-9]{1,2}'
    total_regex = r'(合計|小計|ノヽ言十|消費税).*[0-9]*'
    item_price_regex = r'([0-9]|\*|＊|※|[a-z])\Z'  # 末尾が数字か軽減税率の記号かアルファベット（数字が読み取れていない場合用）
    price_regex = r'([0-9]|[a-z])*\Z'  # アルファベットは数値が誤って変換されていることがあるため
    reduced_tax_regex = r'(\*|＊|※)'
    top_num_regex = r'^[0-9]*'

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


    def get_item_price_reduced_tax_rate(self, receipt_content):
        start_low = [receipt_content.index(s) for s in receipt_content if re.search(self.date_regex, s)][0] + 1  # payment_dateの次の行が開始行とする
        end_low = [receipt_content.index(s) for s in receipt_content if re.search(self.total_regex, s)][0]

        item_and_price = receipt_content[start_low:end_low]
        item_and_price = [s for s in item_and_price if re.search(self.item_price_regex, s)]  
        
        reduced_tax_rate = [1 if re.search(self.reduced_tax_regex, s) else 0 for s in item_and_price]
        item_and_price = [re.sub(self.reduced_tax_regex, r'', s) for s in item_and_price]  # 軽減税率の判定終わったらその記号は取り除く

        item = [re.sub(self.price_regex, r'', s) for s in item_and_price]
        item = [re.sub(self.top_num_regex, r'', s) for s in item]
        item = [re.sub(r'\\*\Z', r'', s) for s in item]
        price = [re.search(self.price_regex, s).group() for s in item_and_price]
        return item, price, reduced_tax_rate


    def get_tax_excluded_included(self, receipt_content):
        excluded_flg = [1 for s in receipt_content if re.search(r'外税',s)]
        tax_excluded = 1 if len(excluded_flg)>=1 else 0
        return tax_excluded


def main():
    input_file_list = get_input_file_list()
    input_file = input_file_list[3]
    
    ocr = OcrReceipt()
    receipt_content = ocr.ocr(input_file)
    payment_date = ocr.get_payment_date(receipt_content)
    item, price, reduced_tax_rate = ocr.get_item_price_reduced_tax_rate(receipt_content)
    tax_excluded = ocr.get_tax_excluded_included(receipt_content)

    return payment_date, item, price, reduced_tax_rate, tax_excluded, input_file


if __name__ == '__main__':
    main()