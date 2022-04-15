from tdatlib import treemap_deploy


if __name__ == "__main__":
    market_map = treemap_deploy()
    market_map.to_js()

    # run_on = 'network'
    # if run_on == 'local':
    #     market = market_kr()
    #     if market.etf_check():
    #         market.etf_excel2csv()