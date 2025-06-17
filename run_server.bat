@echo off
echo Activating 'utesocial' environment and starting Django development server with Daphne...

REM Kích hoạt Conda environment
call conda activate utesocial

REM Thiết lập biến môi trường cho Django
set "DJANGO_SETTINGS_MODULE=UTESocialNetwork.settings"
set "PYTHONPATH=%PYTHONPATH%;%CD%"

REM Chạy Daphne server
call daphne -b 0.0.0.0 -p 8000 UTESocialNetwork.asgi:application