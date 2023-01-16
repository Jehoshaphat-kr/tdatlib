from snob import market as treemap

RUN_TREEMAP = True
CHK_ETF     = False

if __name__ == "__main__":
    new_treemap = treemap.marketmap

    if RUN_TREEMAP:
        new_treemap.collect()
        new_treemap.pd2js()
