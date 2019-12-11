# Gohlke Grabber

Simple script to download .whl packages from the pre-built Python packages at https://www.lfd.uci.edu/~gohlke/pythonlibs.

Christoph Gohlke maintains 32-bit and 64-bit binaries for many popular scientific Python packages. These can save you some trouble in cases where getting the package from PyPI (using `pip install package_name`) causes pip to try and build underlying C or C++ code. This can of course be made to work on Windows, but requires the installation and configuration of a C/++ compiler and libraries - both of which come standard with a Linux installation, but not with Windows.

So, if you have issues installing a package, you trust Gohlke's build, and you want something easy that helps automate the download, grab a copy of [gohlke_grabber.py](gohlke-grabber/gohlke_grabber.py) and call it like shown below or in [download.py](example/download.py).

Of course, once you have a wheel (a file with the `.whl` extension), you can install it using:
```cmd
pip install path\to\saved\location\name.whl
```

## Usage

When you create a `GohlkeGrabber`, it automatically grabs the web page and figures out all the packages on offer. Of course, this requires an active connection to the web (the first time at least, see below). 

You can list them like so:
```python
from gohlkegrabber import GohlkeGrabber
gg = GohlkeGrabber()
print(list(gg.packages))
```
Note that `.packages` is a `dict` - of course you can just use the dictionary directly and the data therein yourself as well. For example, this is what the start of the `numpy` entry looks like:
```python
{
  'numpy‑1.16.5+mkl‑cp27‑cp27m‑win32.whl': {
    'link': 'https://download.lfd.uci.edu/pythonlibs/t7epjj8p/numpy-1.16.5+mkl-cp27-cp27m-win32.whl',
    'version': '1.16.5+mkl',
    'build': None,
    'python': '2.7',
    'abi': 'cp27m',
    'platform': 'win32'
  },
  'numpy‑1.16.5+mkl‑cp27‑cp27m‑win_amd64.whl': ...
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