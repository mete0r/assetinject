# -*- coding: utf-8 -*-
#
#   assetinject : inject assets into HTML documents
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
Usage:
    assetinject <assets.json> [<index.html>]

'''
from contextlib import contextmanager
from shutil import copyfileobj
from tempfile import mkstemp
import json
import os
import sys

from docopt import docopt


def main():
    args = docopt(__doc__)

    with file(args['<assets.json>']) as f:
        assets = json.load(f)

    path = args['<index.html>']
    with open_output(path) as g:
        with open_input(path) as f:
            replaced = replace_assets_region(f, assets)
            g.writelines(replaced)


def open_input(path):
    if path:
        return file(path)
    else:
        return sys.stdin


@contextmanager
def open_output(path):
    if path:
        fd, tmp_path = mkstemp()
        os.close(fd)
        try:
            with file(tmp_path, 'w') as f:
                yield f
            with file(tmp_path, 'r') as f:
                with file(path, 'r+') as g:
                    copyfileobj(f, g)
                    g.truncate()
        finally:
            os.unlink(tmp_path)
    else:
        with sys.stdout as f:
            yield f


def replace_assets_region(lines, assets):
    region = False
    for line in lines:
        if not region and 'BEGIN assets' in line:
            yield line
            region = True
            continue
        elif region and 'END assets' in line:
            for x in make_assets_html(assets):
                yield x
            yield line
            region = False
        elif not region:
            yield line
    if region:
        for x in make_assets_html(assets):
            yield x


def make_assets_html(assets):
    for css in assets['css']:
        yield '<link rel="stylesheet" href="%s" />\n' % css
    for js in assets['js']:
        yield '<script type="text/javascript" src="%s"></script>\n' % js
