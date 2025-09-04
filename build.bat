@echo off
echo ================================================
echo           PAPIWEB Editor - Build Script
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado
    echo Por favor, instale Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Crear y activar entorno virtual
echo Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

REM Construir versión GUI
echo.
echo Construyendo PAPIWEB Editor GUI...
pyinstaller --clean ^
    --onefile ^
    --windowed ^
    --name PAPIWEB_Editor_GUI ^
    papiweb_editor.py

REM Construir versión Consola
echo.
echo Construyendo PAPIWEB Editor Console...
pyinstaller --clean ^
    --onefile ^
    --name PAPIWEB_Editor_Console ^
    papiweb_editor_console.py

echo.
echo ================================================
echo Construcción completada!
echo Los ejecutables se encuentran en la carpeta 'dist':
echo - PAPIWEB_Editor_GUI.exe
echo - PAPIWEB_Editor_Console.exe
echo ================================================

REM Desactivar entorno virtual
deactivate

pause
