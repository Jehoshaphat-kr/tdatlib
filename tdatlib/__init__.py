"""
Library Structure

tdatlib
  $ fetch
    $ archive
      * __init__.py
      $ category
        * __ETF.xlsx
        * __THM.xlsx
        * etf.csv
        * theme.csv
        * wi26.csv
        * wics.csv
      $ common
        * backup-icm.csv
        * backup-perf.csv
        * icm.csv
        * perf.csv
      $ treemap
        $ deploy
          $ js
            * /* Deploy java-scripts */
          * suffix.js


"""
from tdatlib.interface.treemap import deploy as treemap_deploy
from tdatlib.fetch.market import check_etf_handler
import os


def tree(path:str):
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = '\t' * level
        print('{}{}/'.format(indent, os.path.basename(root)))
        sub_indent = '\t' * (level + 1)
        for f in files:
            if not f.endswith('.pyc') and not f.endswith('.xlsx'):
                print('{}{}'.format(sub_indent, f))


def implement(__dir):

    return

if __name__ == "__main__":
    tree(os.path.dirname(__file__))