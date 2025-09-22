@echo off
echo Loading environment variables...
for /F "tokens=1,2 delims==" %%G in (.env) do set %%G=%%H
echo Environment variables loaded.
