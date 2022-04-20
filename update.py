from tdatlib import treemap_deploy, check_etf_handler


if __name__ == "__main__":
    run_on = 'network'
    if run_on == 'local':
        check_etf_handler(base='csv')

    market_map = treemap_deploy()
    market_map.to_js()