@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 日志查看脚本 - Windows版本

set LOG_DIR=backend\logs

REM 检查日志目录是否存在
if not exist "%LOG_DIR%" (
    echo [错误] 日志目录不存在 (%LOG_DIR%)
    echo 请先启动服务以生成日志文件
    pause
    exit /b 1
)

:menu
cls
echo.
echo ========================================
echo   日志查看工具
echo ========================================
echo.
echo 请选择要查看的日志类型:
echo.
echo   1) 所有日志 (app.log)
echo   2) 错误日志 (error.log)
echo   3) 请求日志 (request.log)
echo   4) OCR日志 (ocr.log)
echo   5) LLM日志 (llm.log)
echo   6) 查看所有日志文件
echo   0) 退出
echo.

set /p choice=请选择 [0-6]: 

if "%choice%"=="1" goto view_app
if "%choice%"=="2" goto view_error
if "%choice%"=="3" goto view_request
if "%choice%"=="4" goto view_ocr
if "%choice%"=="5" goto view_llm
if "%choice%"=="6" goto view_all
if "%choice%"=="0" goto exit
goto menu

:view_app
cls
echo [查看] 所有日志
echo 按 Ctrl+C 退出
echo.
if exist "%LOG_DIR%\app.log" (
    powershell -Command "Get-Content '%LOG_DIR%\app.log' -Wait -Tail 50"
) else (
    echo 日志文件不存在，等待生成...
    timeout /t 2 >nul
    goto view_app
)
goto menu

:view_error
cls
echo [查看] 错误日志
echo 按 Ctrl+C 退出
echo.
if exist "%LOG_DIR%\error.log" (
    powershell -Command "Get-Content '%LOG_DIR%\error.log' -Wait -Tail 50"
) else (
    echo 日志文件不存在，等待生成...
    timeout /t 2 >nul
    goto view_error
)
goto menu

:view_request
cls
echo [查看] 请求日志
echo 按 Ctrl+C 退出
echo.
if exist "%LOG_DIR%\request.log" (
    powershell -Command "Get-Content '%LOG_DIR%\request.log' -Wait -Tail 50"
) else (
    echo 日志文件不存在，等待生成...
    timeout /t 2 >nul
    goto view_request
)
goto menu

:view_ocr
cls
echo [查看] OCR日志
echo 按 Ctrl+C 退出
echo.
if exist "%LOG_DIR%\ocr.log" (
    powershell -Command "Get-Content '%LOG_DIR%\ocr.log' -Wait -Tail 50"
) else (
    echo 日志文件不存在，等待生成...
    timeout /t 2 >nul
    goto view_ocr
)
goto menu

:view_llm
cls
echo [查看] LLM日志
echo 按 Ctrl+C 退出
echo.
if exist "%LOG_DIR%\llm.log" (
    powershell -Command "Get-Content '%LOG_DIR%\llm.log' -Wait -Tail 50"
) else (
    echo 日志文件不存在，等待生成...
    timeout /t 2 >nul
    goto view_llm
)
goto menu

:view_all
cls
echo [日志文件列表]
echo.
for %%f in ("%LOG_DIR%\*.log") do (
    echo   %%~nxf
)
echo.
pause
goto menu

:exit
echo 退出
exit /b 0

