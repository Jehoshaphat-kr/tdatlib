from tdatlib.dataset import treemap_deploy, is_etf_latest


if __name__ == "__main__":

    # is_etf_latest()
    market_map = treemap_deploy()
    market_map.to_js()