import re
import argparse
import operator
from itertools import zip_longest
from pathlib import Path
from urllib import request
from lxml import html
from io import BytesIO
from sys import version_info
from urllib.error import HTTPError


def _compare_version_parts(op, p1, p2):
    matches = [re.match(r'(\d*)(.*)', p) for p in [p1, p2]]
    if not all(matches):
        raise SyntaxError(f'Unexpected version part {p1}, {p2}')
    return (op(int(matches[0].group(1)), int(matches[1].group(1))) or
            (matches[0].group(1) == matches[1].group(1) and op(matches[0].group(2), matches[1].group(2))))


def version_compare(v1: str, compare_operator, v2: str = None):
    """
    Determines Boolean value for when the compare operator is applied to the version strings
    :param v1: a version string of the form x.y[.z]
    :param compare_operator: any of '>', '<', '==', '<=', '>='
    :param v2: a version string of the form x.y[.z]
    :return: bool, e.g. '1.2', '>=', '0.9' would be True
    """
    if not v1:
        return False

    # if compare_operator has both the operator and the version to compare to e.g. '<=1.0'
    if v2 is None:
        match = re.match('([<>=]+)(.*)', compare_operator)
        if not match:
            raise SyntaxError(f'{compare_operator} is not a valid combination of operator and version string.')
        compare_operator, v2 = match.group(1), match.group(2)

    op = \
        operator.eq if compare_operator == '==' else \
        operator.gt if compare_operator == '>' else \
        operator.lt if compare_operator == '<' else \
        operator.lt if compare_operator == '<=' else \
        operator.gt if compare_operator == '>=' else None

    if op is None:
        raise SyntaxError(f'{compare_operator} is not a valid operator.')

    v1 = v1.split('.')
    v2 = v2.split('.')

    for p1, p2 in zip_longest(v1, v2, fillvalue='0'):
        if _compare_version_parts(op, p1, p2) and compare_operator != '==':
            return True
        elif p1 != p2:
            return False

    return compare_operator in ['==', '>=', '<=']


class GrabError(Exception):
    pass


class GohlkeGrabber:
    def url_open(self, url):
        response = request.urlopen(request.Request(url, headers={'User-Agent': self.user_agent}))
        return response

    def url_retrieve(self, url, filename):
        response = request.urlopen(request.Request(url, headers={'User-Agent': self.user_agent}))
        with open(filename, 'wb') as f:
            f.write(response.read())

    def __init__(self, cached=None):
        """
        When created, the GohlkeGrabber downloads the listed packages on https://www.lfd.uci.edu/~gohlke/pythonlibs
        :param cached: when provided, index will be loaded from this file if it exists, or written to it after download
        """
        self.index_root = 'https://www.lfd.uci.edu/~gohlke/pythonlibs'
        self.download_root = 'https://download.lfd.uci.edu/pythonlibs/'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/84.0.4147.105 Safari/537.36'

        self.index = None
        self.packages = {}
        self._cached = cached
        self.last_retrieve = None
        if self._cached and Path(self._cached).is_file():
            with open(self._cached, 'rb') as f:
                self.index = f.read()
                self._reread_packages()
        else:
            self.reload()

    def __getitem__(self, item):
        return self.packages[item]

    def reload(self):
        """
        Calling will force a reload of the index off the website, even if it was loaded from cache previously
        :return: None
        """
        req = request.Request(self.index_root, headers={'User-Agent': 'custom'})
        response = request.urlopen(req)
        self.index = response.read()
        if self._cached:
            with open(self._cached, 'wb') as f:
                f.write(self.index)
        self._reread_packages()

    def _get_dl_info(self, js_link):
        def dl1(ml, mi):
            lnk = self.download_root
            for j in range(len(mi)):
                lnk += chr(ml[ord(mi[j]) - 47])
            return lnk

        def dl(ml, mi):
            mi = mi.replace('&lt;', '<')
            mi = mi.replace('&#62;', '>')
            mi = mi.replace('&#38;', '&')
            return dl1(ml, mi)

        match = re.search(r'dl\(\[(.*)], "(.*?)"', js_link)
        if match:
            link = dl(list(map(int, match.group(1).split(','))), match.group(2))
            parts = Path(link).stem.split('-')
            has_build_skip = 1 if parts[2][0].isdigit() else 0
            return {
                'link': link,
                'version': parts[1],
                'build': parts[2] if has_build_skip else None,
                'python': (lambda x: f'{x[2]}.{x[3:]}')(parts[2 + has_build_skip]),
                'abi': parts[3 + has_build_skip],
                'platform': parts[4 + has_build_skip]
            }
        else:
            # malformed link!
            return None

    def _reread_packages(self):
        root = html.parse(BytesIO(self.index))
        self.packages = {}
        for list_item in root.xpath('//ul[@class="pylibs"]/li[a[@id]]'):
            identifier = str(list_item.xpath('a/@id')[0])
            if identifier == 'misc':
                # stopping at misc, miscellaneous not supported
                break
            self.packages[identifier] = {
                anchor.text: self._get_dl_info(str(anchor.xpath('@onclick')[0]))
                for anchor in [li for li in list_item.xpath('ul/li/a') if Path(li.text).suffix == '.whl']
            }

    def retrieve(self, save_location, identifier,
                 overwrite=False, version=None, build=None, python=None, abi=None, platform='win_amd64'):
        """
        Download a wheel for a specific package
        :param save_location: directory to save the downloaded package to (if any)
        :param identifier: the package identifier, the key in self.packages
        :param overwrite: whether to overwrite the file to download, if it exists
        :param version: a specific version, if multiple are available; None results in the most recent
        :param build: a specific build, or the most recent if None
        :param python: a specific python version, or the current if None (pass 'last' for most recent)
        :param abi: a specific python ABI, or the 'm' ABI matching the python version if None
        :param platform: either 'win32' or 'win_amd64' (the default)
        :return: a dict with the actual values for all the function parameters for the downloaded package
        """
        if identifier not in self.packages:
            raise GrabError(f'Could not download "{identifier}", '
                            f'possibly it is not available, or in the "Misc" category.')
        versions = self.packages[identifier]
        best_match = None
        if python == 'last':
            python = None
        elif python is None:
            python = f'{version_info.major}.{version_info.minor}'
        for _, a in versions.items():
            if version:
                if version[0] in '>=<':
                    if version[1] == '=':
                        if not version_compare(a['version'], version[:2], version[2:]):
                            continue
                    else:
                        if not version_compare(a['version'], version[0], version[1:]):
                            continue
                elif a['version'] != version:
                    continue
            if build and a['build'] != build:
                continue
            if python and a['python'] != python:
                continue
            if abi and a['abi'] != abi:
                continue
            if a['platform'] != platform:
                continue
            if best_match:
                if not python and version_compare(a['python'], '>', best_match['python']):
                    best_match = a
                elif version_compare(a['version'], '>', best_match['version']):
                    best_match = a
                elif (version_compare(a['version'], '==', best_match['version']) and
                        version_compare(a['build'], '>', best_match['build'])):
                    best_match = a
            else:
                best_match = a

        if best_match is not None:
            p = Path(save_location) / Path(best_match['link']).name
            if not p.is_file() or overwrite:
                opener = request.build_opener()
                opener.addheaders = [('User-agent', 'Custom')]
                request.install_opener(opener)
                self.last_retrieve = best_match['link']
                request.urlretrieve(self.last_retrieve, p)
        else:
            p = None

        return p, best_match


def cli_entry_point():
    parser = argparse.ArgumentParser(description='Retrieve pre-built binaries'
                                                 ' from https://www.lfd.uci.edu/~gohlke/pythonlibs')
    parser.add_argument('save_location', help='Path to save the wheel to, use "." for current directory.')
    parser.add_argument('identifier', help='Name of the package to download, e.g. "numpy"')
    parser.add_argument('-o', '--overwrite', help='Overwrite existing files',
                        action='store_const', const=True, default=False)
    parser.add_argument('-v', '--version', help='Version of the package to download,'
                                                ' e.g. "1.18", or "<1.19", most recent if none')
    parser.add_argument('-b', '--build', help='Specific build of the package to download, most recent if none')
    parser.add_argument('-p', '--python', help='Python version required, e.g. "3.6", "<3.7", or "last"')
    parser.add_argument('-a', '--abi', help='A specific python ABI, or the "m" ABI matching the Python version if none')
    parser.add_argument('-pf', '--platform', help='Either "win32" or "win_amd64" (the default)', default='win_amd64')
    parser.add_argument('-c', '--cache', help='File path to store a cached copy (html) of the index,'
                                              ' not caching if none')
    parser.add_argument('-x', '--bare', help='Only print the name of the resulting wheel (if any, for capture)',
                        action='store_const', const=True)

    args = parser.parse_args()
    cache_file = args.cache
    bare = bool(args.bare) if args.bare is not None else False
    del args.cache
    del args.bare

    if not bare:
        print('Getting index...')
    gg = GohlkeGrabber(cached=cache_file)
    if not bare:
        print(f'Attempting to download package "{args.identifier}" to "{args.save_location}" ...')
    try:
        p, best_match = gg.retrieve(**vars(args))
        if best_match is None:
            if not bare:
                print('Unable to find a matching package version at https://www.lfd.uci.edu/~gohlke/pythonlibs')
            exit(1)
        else:
            if not bare:
                print(f'Finished download to "{p}"')
            else:
                print(p)
    except GrabError as e:
        print(e)
    except HTTPError as e:
        if not bare:
            print(f'Error trying to download: {gg.last_retrieve}, {e}')
        exit(1)


if __name__ == '__main__':
    cli_entry_point()
