#!/usr/bin/env bash
# Linux/macOS: gera avx2_square.so (usa -mavx2 se o processador tiver AVX2)
set -e
FLAGS="-O2 -shared -fPIC"
if grep -q avx2 /proc/cpuinfo 2>/dev/null; then
  FLAGS="$FLAGS -mavx2"
  echo "[+] AVX2 detectado — compilando com -mavx2"
else
  echo "[!] Sem AVX2 — compilando versão escalar"
fi
gcc $FLAGS -o avx2_square.so avx2_square.c
echo "[+] Pronto: ./avx2_square.so"
