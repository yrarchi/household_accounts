import cv2
import math
import numpy as np
import os
import sys

from get_file_path_list import get_input_path_list


class GetReceiptContours:
    interim_relative_path = "../img/interim"
    interim_path = os.path.join(os.path.dirname(__file__), interim_relative_path)

    def __init__(self, input_path):
        self.input_file = cv2.imread(input_path)
        self.input_filename = os.path.splitext(os.path.basename(input_path))[0]
        self.height, self.width, _ = self.input_file.shape
        self.img_size = self.height * self.width
        self.binary_img = self.binarize()
        self.contours = self.find_contours()
        self.approx_contours = self.approximate_contours()
        self.rectangle_contours = self.limited_to_rectangles()
        self.draw_contours()

    def binarize(self):
        gray_img = cv2.cvtColor(self.input_file, cv2.COLOR_BGR2GRAY)
        binary_img = cv2.adaptiveThreshold(
            gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 255, 2
        )
        modified_binary_img = cv2.medianBlur(binary_img, 9)
        return modified_binary_img

    def find_contours(self):
        _, th1 = cv2.threshold(self.binary_img, 127, 255, cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        copy_input_file = self.input_file.copy()
        draw_contours_file = cv2.drawContours(
            copy_input_file, contours, -1, (0, 0, 255, 255), 10
        )
        cv2.imwrite(
            "{}/write_all_contours_{}.png".format(
                self.interim_path, self.input_filename
            ),
            draw_contours_file,
        )
        return contours

    def approximate_contours(self):
        approx_contours = []
        for i, cnt in enumerate(self.contours):
            arclen = cv2.arcLength(cnt, True)
            area = cv2.contourArea(cnt)
            if arclen != 0 and self.img_size * 0.02 < area < self.img_size * 0.9:
                approx_contour = cv2.approxPolyDP(
                    cnt, epsilon=0.01 * arclen, closed=True
                )
                approx_contours.append(approx_contour)
        return approx_contours

    def limited_to_rectangles(self):
        def get_max_abs_cosine(contour):
            cos_list = []
            for i in range(4):
                points = [contour[i], contour[(i + 1) % 4], contour[(i + 3) % 4]]
                vec_1 = points[1] - points[0]
                vec_2 = points[2] - points[0]
                norm_1 = np.linalg.norm(vec_1)
                norm_2 = np.linalg.norm(vec_2)
                inner_product = np.inner(vec_1, vec_2)
                cos = inner_product / (norm_1 * norm_2)
                cos_list.append(cos)
            return max(list(map(abs, cos_list)))

        rectangle_contours = []
        for contour in self.approx_contours:
            if len(contour) == 4:  # 頂点が4点の輪郭のみにする
                max_abs_cos = get_max_abs_cosine(contour)
                if max_abs_cos < math.cos(math.radians(80)):  # なす角が80°~100°のみにする
                    rectangle_contours.append(contour)
        return rectangle_contours

    def draw_contours(self):
        if len(self.rectangle_contours) == 0:
            sys.exit("画像からレシートの外枠を検知できなかったので終了します")
        copy_input_file = self.input_file.copy()
        draw_contours_file = cv2.drawContours(
            copy_input_file, self.rectangle_contours, -1, (0, 0, 255, 255), 10
        )
        cv2.imwrite(
            "{}/write_contours_{}.png".format(self.interim_path, self.input_filename),
            draw_contours_file,
        )


class GetEachReceiptImg(GetReceiptContours):
    def __init__(self, input_path):
        super().__init__(input_path)
        for i in range(len(self.rectangle_contours)):
            receipt_no = i
            self.sorted_corner_list = self.get_sorted_corner_list(receipt_no)
            self.width, self.height = self.get_length_receipt()
            self.projective_transformation(receipt_no)

    def get_sorted_corner_list(self, receipt_no):
        corner_list = [self.rectangle_contours[receipt_no][i][0] for i in range(4)]
        corner_x = list(map(lambda x: x[0], corner_list))
        corner_y = list(map(lambda x: x[1], corner_list))

        west_1, west_2 = (
            corner_x.index(sorted(corner_x)[0]),
            corner_x.index(sorted(corner_x)[1]),
        )  # 左側2点のインデックス
        if west_1 == west_2:
            west_1, west_2 = [
                i for i, x in enumerate(corner_x) if x == sorted(corner_x)[0]
            ]
        north_west = (
            west_1 if corner_y[west_1] > corner_y[west_2] else west_2
        )  # 左上の点のインデックス
        south_west = west_2 if west_1 == north_west else west_1

        east_1, east_2 = [i for i in range(len(corner_x)) if i not in [west_1, west_2]]
        north_east = east_1 if corner_y[east_1] > corner_y[east_2] else east_2
        south_east = east_2 if east_1 == north_east else east_1

        sorted_corner_list = [
            corner_list[i] for i in [north_west, south_west, south_east, north_east]
        ]  # 左上から反時計回り
        return sorted_corner_list

    def get_length_receipt(self):
        width = np.linalg.norm(self.sorted_corner_list[0] - self.sorted_corner_list[3])
        height = np.linalg.norm(self.sorted_corner_list[0] - self.sorted_corner_list[2])
        return width, height

    def projective_transformation(self, receipt_no):
        pts_before = np.float32(self.sorted_corner_list)
        pts_after = np.float32(
            [[0, self.height], [0, 0], [self.width, 0], [self.width, self.height]]
        )
        M = cv2.getPerspectiveTransform(pts_before, pts_after)
        dst = cv2.warpPerspective(
            self.input_file, M, (int(self.width), int(self.height))
        )
        cv2.imwrite(
            "{}/each_receipt/receipt_{}_{}.png".format(
                self.interim_path, self.input_filename, receipt_no
            ),
            dst,
        )


def main():
    input_path_list = get_input_path_list(
        relative_path="../img/unprocessed", extension="jpg"
    )
    input_path = input_path_list[0]  # 現状、読み取り対象の画像は1枚しか対応していないため
    print("処理中...")
    GetReceiptContours(input_path)
    GetEachReceiptImg(input_path)


if __name__ == "__main__":
    main()
