@echo off
python setup.py sdist bdist_wheel
echo If build succeeds and tests well, wheel is available in `dist`
