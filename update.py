from tdatlib import treemap_deploy


if __name__ == "__main__":
    market_map = treemap_deploy()
    market_map.to_js()