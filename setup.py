from distutils.core import setup
setup(
  name='gohlkegrabber',
  packages=['gohlkegrabber'],
  version='0.2.1',
  license='MIT',
  description='Simple script to download .whl packages from www.lfd.uci.edu/~gohlke/pythonlibs.',
  author='BMT, Jaap van der Velde',
  author_email='jaap.vandervelde@bmtglobal.com',
  url='https://github.com/jaapvandervelde/gohlkegrabber',
  download_url='https://github.com/jaapvandervelde/gohlkegrabber/archive/0.2.1.tar.gz',
  keywords=['package', 'download', 'gohlke', 'wheel'],
  install_requires=[
      'lxml>=4.4.2'
  ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
  ],
)
