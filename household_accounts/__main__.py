import ocr
import cut_out_images
import gui_each_receipt
from gui_make_pages import MakePages
from gui_show_receipt_contours import MakePage1 


cut_out_images.main()
gui = MakePages()
MakePage1(gui.page1, gui.page2)

payment_date, item, price, reduced_tax_rate_flg, tax_excluded, input_file = ocr.main()
gui_each_receipt.main(payment_date, item, price, reduced_tax_rate_flg, tax_excluded, input_file, gui.page2, gui)

gui.mainloop()
