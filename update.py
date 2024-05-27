
if __name__ == "__main__":

    # from snob.market.core import etf
    # etf.islatest()

    from snob import market as treemap
    new_treemap = treemap.marketmap
    new_treemap.collect()
    new_treemap.pd2js()
