import ocr
import cut_out_images
from gui_make_pages import MakeGuiScreen
from gui_show_receipt_contours import MakeFirstPage
from get_file_path_list import get_input_path_list


cut_out_images.main()
input_path_list = get_input_path_list(relative_path='../img/interim/each_receipt', extension='png')
ocr_results = ocr.main(input_path_list)
gui = MakeGuiScreen(input_path_list, ocr_results)
MakeFirstPage(gui)

gui.mainloop()