import pyocr
import pyocr.builders
import re
import time
from datetime import datetime
from PIL import Image

from get_file_path_list import get_input_path_list
from edit_csv import csv_reader


class OcrReceipt:
    date_regex = (
        r"(([0-9]|[a-z]|[A-Z]){4,})(/|-|年)*"
        r"(([0-9]|[a-z]|[A-Z]){1,2})(/|-|月)*"
        r"(([0-9]|[a-z]|[A-Z]){1,2})日*"
        r"(\(.+\))*"  # 曜日
        r"([0-9]{1,2}:[0-9]{1,2})*"  # 時刻
    )  # 英字は数字が読み取れていない場合用
    total_regex = r"(合計|小計|言十|消費税|対象計|釣り*|預か*り|外税).*[0-9]*"
    item_price_regex = (
        r"([0-9]|[a-z]|[A-Z]).{0,2}\Z"  # 末尾が数字か軽減税率の記号か英字（英字は数字が読み取れていない場合用）
    )
    reduced_tax_regex = r"(\*|＊|※|W|w)"
    top_num_regex = r"^[0-9]{3,}"
    tax_ex_regex = r"外税"
    tax_in_regex = r"(内税|内消費税等)"
    separator = r"区切位置"
    discount_regex = r"(割り*引|値引|まとめ買い*)"
    conversion_to_numeric = {
        "O": "0",
        "U": "0",
        "b": "6",
        "Z": "2",
        "<": "2",
        "i": "1",
    }

    def __init__(self, input_file):
        content_en, content = self.ocr(input_file)
        self.payment_date, self.payment_date_row = self.get_payment_date(content)
        self.tax_excluded = self.get_tax_excluded_included(content)
        main_contents = self.get_main_contents(content, content_en)
        self.reduced_tax_rate_flg = self.get_reduced_tax_rate_flg(main_contents)
        self.item, price = self.separate_item_and_price(main_contents)
        self.price = self.modify_price(price)
        self.discount = self.get_discount_list()
        self.exclude_unnecessary_row()

    def ocr(self, input_file):
        tool = pyocr.get_available_tools()[0]
        receipt_ocr = tool.image_to_string(
            Image.open(input_file),
            lang="jpn",
            builder=pyocr.builders.TextBuilder(tesseract_layout=4),
        )

        receipt_content = receipt_ocr.split("\n")
        content_en = []
        content = []
        for row in receipt_content:
            index = [
                r.start()
                for r in re.finditer(r" -*([0-9]|[A-Z]|[a-z])+( .{0, 1})*", row)
            ]
            index_separator_a = [index[-1] if index != [] else len(row)]
            index_separator_b = [row.rfind("\\") if ("\\" in row) else len(row)]
            index_separator = min(index_separator_a + index_separator_b)
            row_en = row[:index_separator] + self.separator + row[index_separator + 1 :]
            row_en = re.sub(r" ", r"", row_en)
            row = re.sub(r" ", r"", row)
            content_en.append(row_en)
            content.append(row)
        return content_en, content

    def get_payment_date(self, content):
        candidate_of_payment_date = [
            re.search(self.date_regex, s).group()
            for s in content
            if re.search(self.date_regex, s)
        ]
        # 一番日付らしい行を購入日として扱う
        points = []
        for value in candidate_of_payment_date:
            point = value.count("/")
            point += value.count("年")
            point += value.count("月")
            point += value.count(":")  # 購入時刻も併記されていることが多い
            point += value.count("(")  # 購入曜日もかっこ書きで併記されていることが多い
            points.append(point)
        payment_date_index = points.index(max(points)) if len(points) > 0 else 0
        payment_date = candidate_of_payment_date[payment_date_index]
        payment_date_row = [content.index(s) for s in content if payment_date in s][0]

        # 曜日と時刻を除外する
        payment_date = re.sub(r"(\(.\).*$|[0-9]{1,2}\:[0-9]{1,2}$)", "", payment_date)

        for before, after in self.conversion_to_numeric.items():
            payment_date = re.sub(before, after, payment_date)

        payment_date = re.sub(r"(年|月|-)", r"/", payment_date)
        payment_date = re.sub(r"[^0-9|^/]", r"", payment_date)

        # 年月日の区切りがない場合や他の数値が結合している場合にある程度整形する
        try:
            split_payment_date = payment_date.split("/")
            len_split_payment_date = list(map(len, split_payment_date))
            if (
                payment_date.count("/") == 1 and len_split_payment_date[1] <= 2
            ):  # 年と月が分割できていない場合
                day = split_payment_date[1]
                month = split_payment_date[0][-2:]
                year = split_payment_date[0][-6:-2]
            if (
                payment_date.count("/") == 1 and len_split_payment_date[1] > 2
            ):  # 月と日が分割できていない場合
                day = split_payment_date[1][-2:]
                month = split_payment_date[1][:-2]
                year = split_payment_date[0][-4:]
            elif (
                payment_date.count("/") == 0 and sum(len_split_payment_date) >= 8
            ):  # 年月日が分割できておらず桁数が多い場合
                day = split_payment_date[0][-2:]
                month = split_payment_date[0][-4:-2]
                year = split_payment_date[0][-8:-4]
            elif (
                payment_date.count("/") == 0 and sum(len_split_payment_date) < 8
            ):  # 年月日が分割できておらず桁数が少ない場合
                day = (
                    split_payment_date[0][-1]
                    if payment_date[-2] > 3
                    else split_payment_date[0][-2:]
                )
                month = (
                    split_payment_date[0][-3:-2]
                    if payment_date[-2] > 3
                    else split_payment_date[0][-3]
                )
                year = split_payment_date[0][:4]
            elif payment_date.count("/") == 2:  # # 年月日が分割できている場合
                day = split_payment_date[2]
                month = split_payment_date[1]
                year = split_payment_date[0][-4:]
            payment_date = "/".join([year, month, day])
            payment_date = datetime.strptime(payment_date, "%Y/%m/%d").strftime(
                "%Y/%m/%d"
            )
        except (ValueError, TypeError):
            pass
        return payment_date, payment_date_row

    def get_tax_excluded_included(self, content):
        tax_excluded_flg = [1 for s in content if re.search(self.tax_ex_regex, s)]
        tax_included_flg = [1 for s in content if re.search(self.tax_in_regex, s)]
        tax_excluded = (
            1 if len(tax_excluded_flg) > len(tax_included_flg) else 0
        )  # 外税判断の文字列が内税判断の文字列を超えた数存在すれば外税とする
        return tax_excluded

    def get_main_contents(self, content, content_en):
        start_low = self.payment_date_row + 1  # payment_dateの次の行が開始行とする
        sum_lows = [content.index(s) for s in content if re.search(self.total_regex, s)]
        end_low = (
            sum_lows[0] if sum_lows != [] else len(content) - 1
        )  # 合計行とみなす列があればその上の列を終了行とし、なければ最後まで含める
        end_low = (
            end_low if start_low <= end_low else len(content) - 1
        )  # レシート冒頭で消費税等total_regexに関する言及がある場合、終了行が開始行より前に来てしまうため
        main_contents = content_en[start_low:end_low]
        main_contents = [
            s for s in main_contents if re.search(self.item_price_regex, s)
        ]
        return main_contents

    def get_reduced_tax_rate_flg(self, main_contents):
        reduced_tax_rate_flg = [
            1 if re.search(self.reduced_tax_regex, s) else 0 for s in main_contents
        ]
        return reduced_tax_rate_flg

    def separate_item_and_price(self, main_contents):
        item_and_price = [
            re.sub(self.reduced_tax_regex, r"", s) for s in main_contents
        ]  # 軽減税率の記号は取り除く
        item = [s[: s.find(self.separator)] for s in item_and_price]  # separatorより左が品目名
        item = [re.sub(self.top_num_regex, r"", s) for s in item]
        price = [
            s[s.find(self.separator) + len(self.separator) :] for s in item_and_price
        ]  # separatorより右が価格
        return item, price

    def modify_price(self, price):
        price = [re.sub(r"(\\|:)", r"", s) for s in price]
        for before, after in self.conversion_to_numeric.items():
            price = [re.sub(before, after, p) for p in price]
        price = [re.sub(r"[^0-9]", r"", p) for p in price]
        return price

    def get_discount_list(self):
        discount = [0] * len(self.item)
        index_discount = [
            i for i, s in enumerate(self.item) if re.search(self.discount_regex, s)
        ]
        if len(index_discount) > 0:
            index_discount.insert(0, -1)
            index_discount = [
                index_discount[i]
                for i in range(1, len(index_discount))
                if index_discount[i - 1] + 1 < index_discount[i]
            ]  # 割引行が連続していたら除外
            for i in index_discount:
                discount[i - 1] = (
                    abs(int(self.price[i])) if len(self.price[i]) > 0 else 0
                )
            for i in sorted(index_discount, reverse=True):  # indexがずれるので上のforループと分けている
                del self.price[i]
                del self.item[i]
                del self.reduced_tax_rate_flg[i]
                del discount[i]
        return discount

    def exclude_unnecessary_row(self):
        def delete_unnecessary_row(index_unnecessary):
            if len(index_unnecessary) > 0:
                for index in sorted(index_unnecessary, reverse=True):
                    del self.price[index]
                    del self.item[index]
                    del self.reduced_tax_rate_flg[index]
                    del self.discount[index]

        index_empty_price = [i for i, p in enumerate(self.price) if p == ""]  # 価格がない
        delete_unnecessary_row(index_empty_price)  # 以下の判定をするために価格がない場合を先に消す
        self.price = list(map(int, self.price))
        index_high_price = [
            i for i, price in enumerate(self.price) if price > 1000000
        ]  # 10万円以上
        index_empty_item = [
            i for i, item in enumerate(self.item) if item == ""
        ]  # 品目名がない
        index_unnecessary = set(index_high_price + index_empty_item)
        delete_unnecessary_row(index_unnecessary)


def levenshtein_distances(input_word, words_history):
    INSERT_COST = 1
    DELETE_COST = 1
    SUBSTITUTE_COST = 1

    distances = []
    len_input = len(input_word)
    for history_word in words_history:
        len_history = len(history_word)
        dp = [[0] * (len_history + 1) for _ in range(len_input + 1)]

        for i in range(len_history + 1):
            dp[0][i] = i * DELETE_COST
        for i in range(len_input + 1):
            dp[i][0] = i * INSERT_COST

        for i_input in range(1, len_input + 1):
            for i_history in range(1, len_history + 1):
                insertion = dp[i_input - 1][i_history] + INSERT_COST
                deletion = dp[i_input][i_history - 1] + DELETE_COST
                substitution = (
                    dp[i_input - 1][i_history - 1]
                    if input_word[i_input - 1] == history_word[i_history - 1]
                    else dp[i_input - 1][i_history - 1] + SUBSTITUTE_COST
                )
                dp[i_input][i_history] = min(insertion, deletion, substitution)
        distance = dp[len_input][len_history] / max(len_input, len_history)
        distances.append(distance)
    return distances


def modify_item_name(items):
    LEVENSHTEIN_THRESHOLD = 0.5

    reader = csv_reader("item_ocr_fix")
    ocr_history = [s[0] for s in reader]
    item_history = [s[1] for s in reader]
    item_fix = []
    for item in items:
        distances = levenshtein_distances(item, ocr_history)
        if min(distances) <= LEVENSHTEIN_THRESHOLD:
            min_distance_index = distances.index(min(distances))
            modify_item = ocr_history[min_distance_index]
            item_fix.append(item_history[ocr_history.index(modify_item)])
        else:
            item_fix.append(item)
    return item_fix


def read_category():
    reader = csv_reader("category_fix")
    item_read = [s[0] for s in reader]
    major_read = [s[1] for s in reader]
    medium_read = [s[2] for s in reader]
    return item_read, major_read, medium_read


def determine_category(item, item_read, major_read, medium_read):
    major_category = major_read[item_read.index(item)] if item in item_read else ""
    medium_category = medium_read[item_read.index(item)] if item in item_read else ""
    return major_category, medium_category


def group_category(items):
    item_read, major_read, medium_read = read_category()
    categories = [
        (determine_category(item, item_read, major_read, medium_read)) for item in items
    ]
    major_categories = [s[0] for s in categories]
    medium_categories = [s[1] for s in categories]
    return major_categories, medium_categories


def summing_up_ocr_results(ocr, item_fix, major_category, medium_category):
    result = {}
    result["payment_date"] = ocr.payment_date
    result["item"] = item_fix
    result["price"] = ocr.price
    result["reduced_tax_rate_flg"] = ocr.reduced_tax_rate_flg
    result["tax_excluded_flg"] = ocr.tax_excluded
    result["discount"] = ocr.discount
    result["major_category"] = major_category
    result["medium_category"] = medium_category
    return result


def indicate_processing_status(no, num):
    process_per = round(no / num * 100, 0)
    process_bar = ("=" * no) + (" " * (num - no))
    print("\r処理状況: [{}] {}%".format(process_bar, process_per), end="")
    time.sleep(0.1)


def main():
    input_path_list = get_input_path_list("../img/interim/each_receipt", "png")
    ocr_results = {}
    for i, input_file in enumerate(input_path_list):
        ocr = OcrReceipt(input_file)
        item_fix = modify_item_name(ocr.item)
        major_category, medium_category = group_category(item_fix)
        ocr_results[input_file] = summing_up_ocr_results(
            ocr, item_fix, major_category, medium_category
        )
        indicate_processing_status(i, len(input_path_list))
    return ocr_results


if __name__ == "__main__":
    main()
