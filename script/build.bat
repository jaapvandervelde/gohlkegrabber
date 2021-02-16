@echo off
python setup.py sdist
echo If build succeeds and tests well install twine and upload:
echo pip install twine
echo twine upload dist/*
