from tdatlib.interface.treemap import deploy as treemap_deploy
from tdatlib.fetch.market import check_etf_handler
import os


def tree(path:str) -> str:
    INDENT, _tree = '\t', str()
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        basename = os.path.basename(root)
        if any([__dir in root for __dir in ['__pycache__', 'deprecate', 'deploy']]):
            continue
        _tree += f'{INDENT * level}{basename}/\n'
        for f in files:
            if f.endswith('.pyc') or f.endswith('.xlsx') or f.endswith('.js') or f.startswith('backup'):
                continue
            _tree += f'{INDENT * (level + 1)}{f}\n'
    return _tree


def implement(path:str):
    return


if __name__ == "__main__":
    print(tree(os.path.dirname(__file__)))