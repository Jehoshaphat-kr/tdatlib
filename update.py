import tdatlib

if __name__ == "__main__":

    # market_map = tdatlib.treemap()
    market_map = tdatlib.treemap(set_date="20220310")
    market_map.to_js()
