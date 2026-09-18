@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ZZMI Mod Manager

echo.
echo   ============================================
echo     ZZMI Mod Guan Jia  (ZZMI Mod Manager)
echo   ============================================
echo.

where python >nul 2>nul
if %errorlevel%==0 goto :runpy
where py >nul 2>nul
if %errorlevel%==0 goto :runpylauncher

echo   [X] 没有找到 Python 3
echo       No Python 3 found on this computer.
echo.
echo   请到 https://www.python.org/downloads/ 下载安装,
echo   安装时务必勾选 "Add python.exe to PATH", 然后重新双击本文件。
echo.
echo   或者直接运行同目录下的 ZZMI-Mod-Manager.exe (免安装版, 推荐)。
echo.
pause
exit /b 1

:runpy
python "%~dp0zzmi_manager.py"
goto :done

:runpylauncher
py -3 "%~dp0zzmi_manager.py"
goto :done

:done
echo.
echo   服务已停止 / stopped.  可以直接关闭这个窗口。
pause
