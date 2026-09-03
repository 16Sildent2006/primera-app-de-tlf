@echo off
echo ========================================================
echo   COMPILANDO MOTOR C/C++ DE ORIENTE (oriente_engine.dll)
echo ========================================================

g++ -std=c++17 -O3 -shared -static -static-libgcc -static-libstdc++ ^
    engine/src/graph.cpp engine/src/pricing.cpp engine/src/c_api.cpp ^
    -I engine/include ^
    -o oriente_engine.dll

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] DLL compilada exitosamente: oriente_engine.dll
) else (
    echo.
    echo [ERROR] Fallo la compilacion.
)
