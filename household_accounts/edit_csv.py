import csv
import datetime
import os


def parse_csv_path(file_name):
    return os.path.join(
        os.path.dirname(__file__), f"../csv/learning_file/{file_name}.csv"
    )


def csv_reader(file_name):
    csv_path = parse_csv_path(file_name)
    with open(csv_path, mode="r") as file:
        reader = [row for row in csv.reader(file)]
    return reader


def write_modified_result(info_places, item_places):
    date = info_places["date"].get()
    shop = info_places["shop"].get()
    today = datetime.datetime.now().strftime("%Y%m%d")
    csv_path = os.path.join(os.path.dirname(__file__), "../csv/{}.csv".format(today))
    with open(csv_path, mode="a") as file:
        required = item_places["required"]
        index_required = [i for i, r in enumerate(required) if r.get() == 1]
        for i in index_required:
            item = item_places["item"][i].get()
            price = item_places["price"][i].get()
            major_category = item_places["major_category"][i].get()
            medium_category = item_places["medium_category"][i].get()
            row = [date, item, price, major_category, medium_category, shop]
            csv.writer(file).writerow(row)


def write_diff_to_csv(csv_path, trans):
    with open(csv_path, mode="r+") as file:
        reader = [tuple(row) for row in csv.reader(file)]
        add_row = [list(s) for s in list(set(trans) - set(reader))]
        csv.writer(file, quoting=csv.QUOTE_NONE, escapechar="\\").writerows(add_row)


def write_item_fixes(item_ocr, item_places):
    item_before = item_ocr
    item_after = [s.get() for s in item_places]
    item_fix = [
        (before, after)
        for before, after in zip(item_before, item_after)
        if before != after != ""
    ]
    csv_path = parse_csv_path("item_ocr_fix")
    write_diff_to_csv(csv_path, item_fix)


def write_category_fixes(item_places, major_category_places, medium_category_places):
    item = [s.get() for s in item_places]
    major = [s.get() for s in major_category_places]
    medium = [s.get() for s in medium_category_places]
    category_fix = [
        (item, major, medium)
        for item, major, medium in zip(item, major, medium)
        if major != "" or medium != ""
    ]
    csv_path = parse_csv_path("category_fix")
    write_diff_to_csv(csv_path, category_fix)
