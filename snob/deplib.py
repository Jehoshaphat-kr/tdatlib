import os


class deplib(object):

    def __init__(self):
        self.base = os.path.dirname(__file__)

    def __tree(self) -> (str, str):
        folders, files = list(), list()
        for _root, _dirs, _files in os.walk(self.base):
            if any([__dir in _root for __dir in ['__pycache__', 'deprecate', 'deploy']]):
                continue

            for d in _dirs:
                if d in ['__pycache__', 'deprecate', 'deploy']:
                    continue
                folder = os.path.join(_root, d).replace(self.base, str()).replace('\\', '/')[1:]
                folders.append(folder)

            for f in _files:
                if f.endswith('.pyc') or f.endswith('.xlsx') or f.endswith('.js') or f.startswith('backup'):
                    continue
                file = os.path.join(_root, f).replace(self.base, str()).replace('\\', '/')[1:]
                files.append(file)
        return str(folders), str(files)

    @property
    def syntax(self) -> str:
        _dirs, _files = self.__tree()

        _  = "from tqdm import tqdm\n"
        _ += "from requests import get\n"
        _ += "import os\n\n\n"
        _ += "router = 'https://raw.githubusercontent.com/Jehoshaphat-kr/tdatlib/master/tdatlib/%s'\n"
        _ += f"dirs = {_dirs}\n"
        _ += f"files = {_files}\n"
        _ += "root = os.path.join(r'./', 'tdatlib')\n"
        _ += "os.makedirs(root, exist_ok=True)\n"
        _ += "for d in dirs:\n"
        _ += "\tos.makedirs(os.path.join(root, d), exist_ok=True)\n"
        _ += "for f in tqdm(files, desc='Importing Library...'):\n"
        _ += "\turl = router % f\n"
        _ += "\twith open(os.path.join(root, f), 'w') as file:\n"
        _ += "\t\tfile.write(get(url).text)\n"
        return _

    def make_impl_file(self, dst:str=str()):
        dst = dst if dst else os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        with open(f'{dst}/impl.py', 'w') as f:
            f.write(self.syntax)
        return


if __name__ == "__main__":
    deployer = deplib()
    deployer.make_impl_file()