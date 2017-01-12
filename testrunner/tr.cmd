@echo off

set solution=%1
set testdir=%2
set testfile=%3
set resdir=%4
set resfile=%5


mkdir tmp
copy %solution% tmp
copy %testdir%\%testfile% tmp
cd tmp
echo "" > __init__.py
python -m unittest -v %testfile% > %resfile% 2>&1
set status=%ERRORLEVEL%
move test_results ..\%resdir%\%resfile%
cd ..
del /s /q tmp
del /q tmp
exit /b %status%