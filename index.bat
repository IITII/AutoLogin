rem AutoCheckIn
setlocal EnableDelayedExpansion
cd %~dp0
python ./index.py -u <username> -p <password>
pause