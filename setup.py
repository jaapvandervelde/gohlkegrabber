import os
import re
from setuptools import setup

__name__ = 'gohlkegrabber'

version_fn = os.path.join(__name__, "_version.py")
__version__ = "unknown"
try:
    version_line = open(version_fn, "rt").read()
except EnvironmentError:
    pass # no version file
else:
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    m = re.search(version_regex, version_line, re.M)
    if m:
        __version__ = m.group(1)
    else:
        print(f'unable to find version in {version_fn}')
        raise RuntimeError(f'If {version_fn} exists, it is required to be well-formed')

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
  name=__name__,
  packages=['gohlkegrabber'],
  version=__version__,
  license='MIT',
  description='Simple script to download .whl packages from www.lfd.uci.edu/~gohlke/pythonlibs.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='BMT, Jaap van der Velde',
  author_email='jaap.vandervelde@bmtglobal.com',
  url='https://github.com/jaapvandervelde/gohlkegrabber',
  download_url='https://github.com/jaapvandervelde/gohlkegrabber/archive/v'+__version__+'.tar.gz',
  keywords=['package', 'download', 'gohlke', 'wheel'],
  install_requires=[
      'lxml>=4.4.2'
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
  entry_points={
    'console_scripts': ['ggrab=gohlkegrabber:cli_entry_point'],
  }
)
