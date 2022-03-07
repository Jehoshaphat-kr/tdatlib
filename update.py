import tdatlib

if __name__ == "__main__":


    # market_map = tdatlib.treemap()
    market_map = tdatlib.treemap(progress='print')
    market_map.to_js()