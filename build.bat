@echo off
rem Windows (MinGW): gera avx2_square.dll
gcc -O2 -mavx2 -shared -o avx2_square.dll avx2_square.c
if exist avx2_square.dll (echo [+] Pronto: avx2_square.dll) else (echo [!] Falha na compilacao)
