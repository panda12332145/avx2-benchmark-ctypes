"""Testes do avx2-benchmark-ctypes."""
import os
import subprocess
import sys
import ctypes

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
LIB = os.path.join(HERE, "avx2_square.so")


def _build():
    src = os.path.join(HERE, "avx2_square.c")
    if not os.path.exists(LIB):
        subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", LIB, src],
                       check=True)


def test_build_and_correctness():
    _build()
    import numpy as np
    lib = ctypes.CDLL(LIB)
    lib.square_avx2.argtypes = [
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_size_t,
    ]
    for n in (1, 7, 8, 9, 1000, 100_003):  # inclui não-múltiplos de 8
        arr = np.random.randint(-1000, 1000, size=n, dtype=np.int32)
        out = np.empty_like(arr)
        lib.square_avx2(arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                        out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                        n)
        assert np.array_equal(out, arr * arr), f"incorret para N={n}"


def test_runner_imports_and_help():
    r = subprocess.run([sys.executable, os.path.join(HERE, "benchmark.py"), "--help"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "Benchmark" in r.stdout + r.stderr


def test_runner_small_run():
    r = subprocess.run([sys.executable, os.path.join(HERE, "benchmark.py"),
                        "--n", "5000", "--repeats", "1"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "NumPy" in r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"✅ {fn.__name__}")
    print(f"\n{len(fns)} testes passaram.")
