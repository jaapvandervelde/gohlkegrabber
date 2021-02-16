@echo off
rmdir dist /s /q
rmdir build /s /q
for /f %%i in ('dir /a:d /s /b *.egg-info') do rmdir /s /q "%%i"
