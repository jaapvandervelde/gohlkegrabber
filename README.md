# Gohlke Grabber

Simple script to download .whl packages from the pre-built Python packages at https://www.lfd.uci.edu/~gohlke/pythonlibs.

Christoph Gohlke maintains 32-bit and 64-bit binaries for many popular scientific Python packages. These can save you some trouble in cases where getting the package from PyPI (using `pip install package_name`) causes pip to try and build underlying C or C++ code. This can of course be made to work on Windows, but requires the installation and configuration of a C/++ compiler and libraries - both of which come standard with a Linux installation, but not with Windows.

So, if you have issues installing a package, you trust Gohlke's build, and you want something easy that helps automate the download, grab a copy of [gohlkegrabber.py](https://github.com/jaapvandervelde/gohlkegrabber/blob/master/gohlkegrabber/gohlkegrabber.py) and call it like shown below or in [download.py](https://github.com/jaapvandervelde/gohlkegrabber/blob/master/example/download.py).

Of course, once you have a wheel (a file with the `.whl` extension), you can install it using:
```cmd
pip install path\to\saved\location\name.whl
```

<i>Please don't bother Christoph Gohlke if there are issues with this tool. If it breaks, that's my fault and you should bother me with it, or ideally propose how to fix it. He just provides a valuable service at no cost and merely deserves credit.</i>

## Installing

```cmd
pip install gohlkegrabber
```

## Dependencies

Dependencies that will be installed :
```
lxml>=4.4.2
```

## Getting Started

### Quick

After installing, to get a recent copy of `gdal`:
```python
from gohlkegrabber import GohlkeGrabber
gg = GohlkeGrabber()
gg.retrieve('c:/temp', 'gdal')
```

Or, directly from the command line:
```commandline
ggrab c:\temp gdal
```
Note that `ggrab` takes the same arguments as the `.retrieve()` method, except that positional arguments come after named arguments, as this is the convention on OS CLIs. For example:
```commandline
ggrab -v 1.18 --platform win32 .\bin numpy
```
The CLI command `ggrab` also takes an additional argument `--cache` if you want to specify a cached index file to use, for example:
```commandline
ggrab --cache c:\temp\cache.html . numpy
```
If you run `ggrab` from the command line, you can also pass `--bare` or `-x` 
```commandline
pip install gohklegrabber
for /f "tokens=*" %i in ('ggrab --bare c:\temp numpy') do set ggrab_last_package=%i
pip install %ggrab_last_package%
```
Or in a batch file:
```commandline
@echo off
pip install gohklegrabber
for /f "tokens=*" %%i in ('ggrab --bare c:\temp numpy') do set ggrab_last_package=%%i
pip install %ggrab_last_package%
```

### In greater detail

When you create a `GohlkeGrabber`, it automatically downloads the index from the website (or reads a cached copy) and figures out all the packages on offer. Of course, this requires an active connection to the web. 

You can list the available packages:
```python
print(list(gg.packages))
```
Note that `.packages` is a `dict` - of course you can just use the dictionary directly and the data therein yourself as well. For example, this is what the start of the `numpy` entry looks like:
```python
{
  'numpy-1.16.5+mkl-cp27-cp27m-win32.whl': {
    'link': 'https://download.lfd.uci.edu/pythonlibs/t7epjj8p/numpy-1.16.5+mkl-cp27-cp27m-win32.whl',
    'version': '1.16.5+mkl',
    'build': None,
    'python': '2.7',
    'abi': 'cp27m',
    'platform': 'win32'
  },
  'numpy-1.16.5+mkl-cp27-cp27m-win_amd64.whl': ...
}
```

To download the latest version (default) of `numpy`, for Windows 64-bit (default), and for the most recent version of Python (default) for which it is available, you would call:
```python
fn, metadata = gg.retrieve(output_folder, 'numpy')
```

`fn` will be the filename of the wheel that was downloaded. `metadata` will be a dictionary with the metadata for the downloaded wheel. Both will be `None` if no package could be downloaded that matched the request. 

An example of what the metadata would look like:
```python
{
  'link': 'https://download.lfd.uci.edu/pythonlibs/t7epjj8p/numpy-1.17.4+mkl-cp38-cp38-win_amd64.whl',
  'version': '1.17.4+mkl',
  'build': None,
  'python': '3.8',
  'abi': 'cp38',
  'platform': 'win_amd64'
}
```
Note that this is just the appropriate entry from the `.packages` `dict`.

To get a copy for a specific Python version (e.g. 2.7), Windows version (e.g. 32-bit) and package version (e.g. '<1.17'), you can provide extra parameters to the call in no particular order:
```python
fn, metadata = gg.retrieve(output_folder, 'numpy', python='2.7', platform='win32', version='<1.17')
```

Any file downloaded will be stored in the `output_folder`. 

If the file already exists, it won't be downloaded again, unless you pass `overwrite=True` to the `.retrieve()` call. 

If you create the GohlkeGrabber with a `cached` parameter, it will save the downloaded web page to that location, or load that file instead of downloading it again, if it already exists.
```python
gg = GohlkeGrabber(cached='work/cache.html')
```

## License

This project is licensed under the MIT license. See [LICENSE.txt](https://github.com/jaapvandervelde/gohlkegrabber/blob/master/LICENSE.txt).


## Change log

0.3.9
- adjusted to change on website where identifiers are now prefixed with `_` 
- added simple matching for partial identifiers

0.3.8
- fixed behaviour to download current Python version of package unless 'last' is specified for '--python'

0.3.6 / 0.3.7
- Changed version import for setup.py, as it was causing dependency problems

0.3.5
- Downgraded Python requirement to 3.6

0.3.4
- Improved message for missing packages

0.3.3
- 'Bare' mode added to capture written wheel
- Project structure cleanup (`script` folder, version location)

0.3.2
- Versioning issues resolved 
- Documentation fix
- Short command line switches

0.3.1
- Added command line tool. Added 'User-Agent' to file retrieve as well as index.

0.3.0
- Flipped default for `python` parameter, favouring the current Python over the most recent

0.2.9
- added a user agent header field, as the site no longer serves a basic Python client

0.2.8
- open release, version conflict
