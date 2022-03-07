import tdatlib

if __name__ == "__main__":

    # market_map = tdatlib.marketMap(debug=True)
    market_map = tdatlib.marketMap(debug=False)
    market_map.to_js()