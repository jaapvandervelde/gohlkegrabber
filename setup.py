from setuptools import setup
from gohlkegrabber import __version__

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
  name='gohlkegrabber',
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
    'Programming Language :: Python :: 3.9',
  ],
  entry_points={
    'console_scripts': ['ggrab=gohlkegrabber:cli_entry_point'],
  }
)
