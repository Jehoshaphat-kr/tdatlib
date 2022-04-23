from tdatlib.interface.treemap import deploy as treemap_deploy
from tdatlib.fetch.market import check_etf_handler
from tdatlib.viewer.stock import view_stock
from tdatlib.viewer.market import view_market
from tdatlib.viewer.compare import view_compare
import os


def tree(path:str) -> (str, str):
    folders, files = str(), str()
    for _root, _dirs, _files in os.walk(path):
        if any([__dir in _root for __dir in ['__pycache__', 'deprecate', 'deploy']]):
            continue

        for d in _dirs:
            if d in ['__pycache__', 'deprecate', 'deploy']:
                continue
            folder = os.path.join(_root, d).replace(path, str()).replace('\\', '/')[1:]
            folders += f"\"{folder}\",\n"

        for f in _files:
            if f.endswith('.pyc') or f.endswith('.xlsx') or f.endswith('.js') or f.startswith('backup'):
                continue
            file = os.path.join(_root, f).replace(path, str()).replace('\\', '/')[1:]
            files += f"\"{file}\",\n"
    return folders, files


def implement(dst:str):
    from tqdm import tqdm
    from requests import get
    router = 'https://raw.githubusercontent.com/Jehoshaphat-kr/tdatlib/master/tdatlib/%s'
    dirs = [
        "fetch",
        "interface",
        "viewer",
        "fetch/archive",
        "fetch/macro",
        "fetch/market",
        "fetch/stock",
        "fetch/archive/category",
        "fetch/archive/common",
        "fetch/archive/treemap",
        "interface/market",
        "interface/stock",
        "interface/treemap",
        "viewer/stock",
    ]
    files = [
        "__init__.py",
        "fetch/__init__.py",
        "fetch/archive/__init__.py",
        "fetch/archive/category/etf.csv",
        "fetch/archive/category/theme.csv",
        "fetch/archive/category/wi26.csv",
        "fetch/archive/category/wics.csv",
        "fetch/archive/common/icm.csv",
        "fetch/archive/common/perf.csv",
        "fetch/macro/__init__.py",
        "fetch/market/common.py",
        "fetch/market/etf.py",
        "fetch/market/perf.py",
        "fetch/market/wise.py",
        "fetch/market/__init__.py",
        "fetch/stock/common.py",
        "fetch/stock/fnguide.py",
        "fetch/stock/__init__.py",
        "interface/compare.py",
        "interface/market.py",
        "interface/__init__.py",
        "interface/stock/ohlcv.py",
        "interface/stock/value.py",
        "interface/stock/__init__.py",
        "interface/treemap/deploy.py",
        "interface/treemap/frame.py",
        "interface/treemap/__init__.py",
        "viewer/common.py",
        "viewer/compare.py",
        "viewer/market.py",
        "viewer/treemap.py",
        "viewer/__init__.py",
        "viewer/stock/ohlcv.py",
        "viewer/stock/value.py",
        "viewer/stock/__init__.py",
    ]
    root = os.path.join(dst, 'tdat')
    os.makedirs(root, exist_ok=True)
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    for f in tqdm(files, desc='Importing Library...'):
        url = router % f
        with open(os.path.join(root, f), 'w') as file:
            file.write(get(url).text)
    return


if __name__ == "__main__":

    # folders, files = tree(os.path.dirname(__file__))
    # print(f'{"=" * 30} FOLDERS {"=" * 30}\n{folders}')
    # print(f'{"=" * 30}  FILES  {"=" * 30}\n{files}')


    implement(dst=r'C:\Users\wpgur\Desktop\TEMP')