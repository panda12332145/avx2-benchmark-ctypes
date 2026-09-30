#!/usr/bin/env python3
"""Benchmark AVX2 (DLL via ctypes) vs NumPy vs Python puro.

Uso:
  python benchmark.py             # N=1_000_000
  python benchmark.py --n 10000000
  python benchmark.py --no-lib     # só NumPy/Python
"""
import argparse
import os
import shutil
import subprocess
import sys
import timeit

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_NAMES = ["avx2_square.dll", "avx2_square.so", "libavx2_square.so"]


def find_lib():
    for name in LIB_NAMES:
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            return path
    return None


def try_build():
    """Compila automaticamente se houver gcc/bash (Linux) ou gcc (Windows)."""
    if sys.platform.startswith("win"):
        if shutil.which("gcc"):
            subprocess.run(["gcc", "-O2", "-mavx2", "-shared",
                            "-o", os.path.join(HERE, "avx2_square.dll"),
                            os.path.join(HERE, "avx2_square.c")], check=False)
    else:
        if shutil.which("gcc") and os.path.exists(os.path.join(HERE, "build.sh")):
            subprocess.run(["bash", os.path.join(HERE, "build.sh")], check=False)
    return find_lib()


def load_lib(path):
    import ctypes
    lib = ctypes.CDLL(path)
    lib.square_avx2.argtypes = [
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_size_t,
    ]
    return lib


def main():
    parser = argparse.ArgumentParser(description="Benchmark AVX2 ctypes")
    parser.add_argument("--n", type=int, default=1_000_000,
                        help="tamanho do vetor (padrão 1.000.000)")
    parser.add_argument("--no-lib", action="store_true",
                        help="não usa a biblioteca (só NumPy/Python)")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    import numpy as np

    n = args.n
    arr = np.arange(1, n + 1, dtype=np.int32)
    expected = (arr * arr).astype(np.int32)

    lib = None
    if not args.no_lib:
        path = find_lib() or try_build()
        if path:
            lib = load_lib(path)
            print(f"[+] Biblioteca carregada: {os.path.basename(path)}")
        else:
            print("[!] Biblioteca não encontrada (compile com build.sh/build.bat)")
            print("    Continuando só com NumPy e Python.\n")

    out = np.empty_like(arr)
    import ctypes
    ptr_in = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    ptr_out = out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

    if lib:
        lib.square_avx2(ptr_in, ptr_out, n)
        ok = np.array_equal(out, expected)
        print(f"{'✅' if ok else '❌'} Corretude AVX2 vs NumPy: {'ok' if ok else 'FALHOU'}")
        t_lib = min(timeit.repeat(lambda: lib.square_avx2(ptr_in, ptr_out, n),
                                  repeat=args.repeats, number=3)) / 3
        print(f"⏱️  AVX2 (ctypes):  {t_lib:.6f}s")

    t_np = min(timeit.repeat(lambda: arr * arr,
                             repeat=args.repeats, number=3)) / 3
    print(f"⏱️  NumPy:          {t_np:.6f}s")

    # Python puro em subconjunto (10k) — senão demora demais
    m = min(10_000, n)
    sample = arr[:m].tolist()
    t_py = min(timeit.repeat(lambda: [x * x for x in sample],
                             repeat=3, number=1)) / 1
    print(f"⏱️  Python puro ({m} itens, extrapolado ×{n // m or 1}): {t_py:.6f}s"
          f" → ~{t_py * (n // m or 1):.4f}s p/ N={n}")

    if lib:
        speedup = t_np / t_lib if t_lib else float("inf")
        print(f"\n🚀 AVX2 via ctypes é {speedup:.2f}× {'mais rápido' if speedup >= 1 else 'mais lento'} que NumPy nesta execução")


if __name__ == "__main__":
    main()
