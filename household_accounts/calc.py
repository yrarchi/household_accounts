import config

def calc_price_tax_in(price_list, discount_list, reduced_tax_rate_flg_list, tax_excluded_flg):
    tax_rate = config.tax_rate
    reduced_tax_rate = config.reduced_tax_rate
    
    trans_price_list = []
    for price in price_list:
        try:
            price = int(price)
        except ValueError:  # 金額を数値として読み取れていない（アルファベット等として認識）場合はいったん0円とする
            price = 0
        trans_price_list.append(price)
    
    discount_list = [int(x) for x in discount_list]
    price_discount_list = [p+d for p, d in zip(trans_price_list, discount_list)]

    price_tax_in_list = []
    if tax_excluded_flg:
        for row, (price, reduced_tax_rate_flg) in enumerate(zip(price_discount_list, reduced_tax_rate_flg_list)):
            row = row + 1
            tax = reduced_tax_rate if reduced_tax_rate_flg else tax_rate
            price_tax_in_list.append(int(price * tax))  # 税込にして端数が出た場合は切り捨てとして扱う
    else:
        price_tax_in_list = trans_price_list
    return price_tax_in_list


def calc_sum_price(price_tax_in_list, required_place):
    required = list(map(lambda x: x.get(), required_place))  # 必要行としてチェックしてある品目のみの合計額を出すため
    required_price_tax_in = [p for p, r in zip(price_tax_in_list, required) if r==1]
    sum_price = sum(required_price_tax_in)
    return sum_price