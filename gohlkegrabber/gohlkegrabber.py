import re
import operator
from pathlib import Path
from urllib import request
from lxml import html
from io import BytesIO


def version_compare(v1_str, compare_operator, v2_str=None):
    """
    Determines Boolean value for when the compare operator is applied to the version strings
    :param v1_str: a version string of the form x.y[.z]
    :param compare_operator: any of '>', '<', '==', '<=', '>='
    :param v2_str: a version string of the form x.y[.z]
    :return: bool, e.g. '1.2', '>=', '0.9' would be True
    """
    if v2_str is None:
        if compare_operator[0] in '<>' and compare_operator[1] != '=':
            compare_operator, v2_str = compare_operator[0], compare_operator[1:]
        else:
            compare_operator, v2_str = compare_operator[0:2], compare_operator[2:]

    op = \
        operator.eq if compare_operator == '==' else \
        operator.gt if compare_operator == '>' else \
        operator.lt if compare_operator == '<' else \
        operator.lt if compare_operator == '<=' else \
        operator.gt if compare_operator == '>=' else None

    if op is None:
        raise SyntaxError(f'Unknown compare operator {compare_operator}')

    v1 = v1_str.split('.')
    v2 = v2_str.split('.')

    for p1, p2 in zip(v1, v2):
        if op(p1, p2) and compare_operator != '==':
            return True
        elif p1 != p2:
            return False

    return compare_operator in ['==', '>=', '<=']


class GohlkeGrabber:
    def __init__(self, cached=None):
        """
        When created, the GohlkeGrabber downloads the listed packages on https://www.lfd.uci.edu/~gohlke/pythonlibs
        :param cached: when provided, the index will be loaded from here if it exists, written after load if it doesn't
        """
        self.index_root = 'https://www.lfd.uci.edu/~gohlke/pythonlibs'
        self.download_root = 'https://download.lfd.uci.edu/pythonlibs/'
        self.index = None
        self.packages = {}
        self._cached = cached
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
        Calling will force a reload of the index, even if it was loaded from cache previously
        :return: None
        """
        response = request.urlopen(self.index_root)
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

        match = re.search(r'dl\(\[(.*)\], "(.*?)"', js_link)
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
        :param python: a specific python version, or the most recent if None
        :param abi: a specific python ABI, or the 'm' ABI matching the python version if None
        :param platform: either 'win32' or 'win_amd64' (the default)
        :return: a dict with the actual values for all the function parameters for the downloaded package
        """
        versions = self.packages[identifier]
        best_match = None
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
                request.urlretrieve(best_match['link'], p)
        else:
            p = None

        return p, best_match
