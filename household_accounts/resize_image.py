import os
from PIL import Image


def resize_img(file_path, resize_width, resize_height):
    img = Image.open(file_path)
    img_width, img_height = img.size
    rate_width = img_width / resize_width
    rate_height = img_height / resize_height

    if abs(rate_width-1) >= abs(rate_height-1):
        resize_img = img.resize((resize_width, int(img_height/rate_width)))
    else:
        resize_img = img.resize((int(img_width/rate_height), resize_height))

    dirname, basename = os.path.split(file_path)
    filename, extension = os.path.splitext(basename)
    resize_file_path = dirname + '/resize/' + filename + '_resize' + extension
    #resize_file_path = file_path[:-4] + '_resize' + extension
    resize_img.save(resize_file_path)
    return resize_file_path