from setuptools import setup

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
  name='gohlkegrabber',
  packages=['gohlkegrabber'],
  version='0.2.9',
  license='MIT',
  description='Simple script to download .whl packages from www.lfd.uci.edu/~gohlke/pythonlibs.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='BMT, Jaap van der Velde',
  author_email='jaap.vandervelde@bmtglobal.com',
  url='https://github.com/jaapvandervelde/gohlkegrabber',
  download_url='https://github.com/jaapvandervelde/gohlkegrabber/archive/v0.2.9.tar.gz',
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
)
