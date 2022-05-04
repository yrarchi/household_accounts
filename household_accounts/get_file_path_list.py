import os
import re
import sys


def get_input_path_list(relative_path, extension):
    current_path = os.path.dirname(__file__)
    input_filename_list = os.listdir(os.path.join(current_path, relative_path))
    filename = r"\.({}|{})$".format(extension, extension.upper())
    input_filename_extension_list = [
        f for f in input_filename_list if re.search(filename, f)
    ]
    if len(input_filename_extension_list) == 0:
        sys.exit("{}ファイルがないため処理を終了します".format(extension))
    input_path_list = list(
        map(
            lambda x: os.path.join(current_path, relative_path, x),
            input_filename_extension_list,
        )
    )
    return input_path_list
