import datetime
import tkinter as tk

def show_last_page(gui):
    gui.change_page()
    today = datetime.datetime.now().strftime('%Y%m%d')
    csv_path = 'csv/{}.csv'.format(today)
    message = '終了しました。読み取ったデータは{}に保存されています。'.format(csv_path)
    message_label = tk.Label(gui.next_page, text=message)
    message_label.pack(anchor='center')
    close_button = tk.Button(gui.next_page, text='閉じる', command=gui.destroy)
    close_button.pack(anchor='s', ipadx=100, ipady=15)