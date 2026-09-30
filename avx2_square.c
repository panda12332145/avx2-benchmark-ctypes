/*
 * avx2_square.c — eleva um vetor de int32 ao quadrado usando AVX2.
 * Compilado com -mavx2, cai para o caminho escalar se __AVX2__ não existir.
 * gcc -O2 -mavx2 -shared -fPIC -o avx2_square.so avx2_square.c   (Linux)
 * gcc -O2 -mavx2 -shared        -o avx2_square.dll avx2_square.c   (MinGW)
 */
#include <stdint.h>
#include <stddef.h>

#ifdef __AVX2__
#include <immintrin.h>
#endif

#if defined(_WIN32)
#define API __declspec(dllexport)
#else
#define API
#endif

API void square_avx2(const int32_t *in, int32_t *out, size_t n) {
#ifdef __AVX2__
    size_t i = 0;
    /* 8 int32 por iteração (256 bits) */
    for (; i + 8 <= n; i += 8) {
        __m256i v = _mm256_loadu_si256((const __m256i *)(in + i));
        _mm256_storeu_si256((__m256i *)(out + i), _mm256_mullo_epi32(v, v));
    }
    for (; i < n; i++) {            /* resto (n não múltiplo de 8) */
        out[i] = in[i] * in[i];
    }
#else
    for (size_t i = 0; i < n; i++) {
        out[i] = in[i] * in[i];
    }
#endif
}
