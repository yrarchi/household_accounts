import datetime
import glob
import os
import tkinter as tk

def show_last_page(gui):
    def show_message():
        today = datetime.datetime.now().strftime('%Y%m%d')
        csv_path = 'csv/{}.csv'.format(today)
        message = '終了しました。読み取ったデータは{}に保存されています。'.format(csv_path)
        message_label = tk.Label(gui.next_page, text=message)
        message_label.pack(anchor='center')
    
    def show_close_button():
        def close_button_function():
            img_delete_path = os.path.join(os.path.dirname(__file__), '../img/interim/**/*.png')
            img_delete_path_list = glob.glob(img_delete_path, recursive=True)
            for p in img_delete_path_list:
                if os.path.isfile(p):
                    os.remove(p)
            gui.destroy()
    
        close_button = tk.Button(gui.next_page, text='閉じる', command=close_button_function)
        close_button.pack(anchor='s', ipadx=100, ipady=15)

    gui.change_page()
    show_message()
    show_close_button()