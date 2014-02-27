@staticmethod\
def parse_float(string_to_parse=""):
    string_to_parse = string_to_parse.strip()
    if (string_to_parse == "NR" or string_to_parse ==""):
        return 0.0
    else:
        return float(string_to_parse)

class Variety:
    name = ""
    minimum_prices = 0.0
    maximum_prices = 0.0
    modal_prices = 0.0
    unit_of_price = ""

    def __init__(self):
        pass

    def new(self, variety, minimum_prices, maximum_prices, modal_prices, unit_of_price):
        self.name = variety
        self.minimum_prices = parse_float(minimum_prices)
        self.maximum_prices = parse_float(maximum_prices)
        self.modal_prices = parse_float(modal_prices)
        self.unit_of_price = unit_of_price
        return self


class Commodity:
    market = ""
    type_of_commodity = ""
    commodity_name = ""
    arrivals = 0.0
    unit_of_arrivals = ""

    import datetime

    date = datetime.datetime.today()
    variety = Variety()

    def __init(self):
        pass

    def new(self, market, type_of_commodity, commodity_name, arrivals, unit_of_arrivals, variety, minimum_prices,
            maximum_prices, modal_prices, unit_of_price, date):
        self.market = market
        self.type_of_commodity = type_of_commodity
        self.commodity_name = commodity_name
        self.arrivals = parse_float(arrivals)
self.unit_of_arrivals = unit_of_arrivals
        self.variety = Variety().new(variety, minimum_prices, maximum_prices, modal_prices, unit_of_price)
        self.date = date
        return self