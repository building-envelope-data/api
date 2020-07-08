REM validation of dbe and dsb

echo TestD04

PING localhost -n 1 >NUL

START validateDbeD04.bat

PING localhost -n 1 >NUL

START validateDsbD04.bat

PING localhost -n 3 >NUL