import datetime
import tkinter as tk

from edit_image import delete_img


def show_last_page(gui):
    def show_message():
        today = datetime.datetime.now().strftime("%Y%m%d")
        csv_path = "csv/{}.csv".format(today)
        message = "終了しました。読み取ったデータは{}に保存されています。".format(csv_path)
        message_label = tk.Label(gui.next_page, text=message)
        message_label.pack(anchor="center")

    def show_close_button():
        def close_button_function():
            delete_img("../img/interim/**/*.png")
            gui.destroy()

        close_button = tk.Button(
            gui.next_page, text="閉じる", command=close_button_function
        )
        close_button.pack(anchor="s", ipadx=100, ipady=15)

    gui.change_page()
    show_message()
    show_close_button()
