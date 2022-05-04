import ocr
import cut_out_receipts
from gui_make_pages import MakeGuiScreen
from gui_show_receipt_contours import MakeFirstPage

cut_out_receipts.main()
ocr_results = ocr.main()
gui = MakeGuiScreen(ocr_results)
MakeFirstPage(gui)
gui.mainloop()
