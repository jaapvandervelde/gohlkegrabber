@echo off
git add .
git commit -m %1
git push
call script/cleanup.bat
call script/build.bat
twine upload dist/*
call script/cleanup.bat
