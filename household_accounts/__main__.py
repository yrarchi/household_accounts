import household_accounts.gui as gui
import household_accounts.ocr as ocr

payment_date, item, price, reduced_tax_rate_flg, tax_excluded, input_file = ocr.main()
gui.main(payment_date, item, price, reduced_tax_rate_flg, tax_excluded, input_file)