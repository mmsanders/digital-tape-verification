#include "audio_oracle.h"

#include <assert.h>
#include <stdint.h>

static void test_overdub(void)
{
    assert(audio_oracle_overdub(32767, 32767) == 32767);
    assert(audio_oracle_overdub(-32768, -32768) == -32768);
    assert(audio_oracle_overdub(32767, -32768) == -1);
    assert(audio_oracle_overdub(100, -99) == 1);
    assert(audio_oracle_overdub(32760, 7) == 32767);
    assert(audio_oracle_overdub(-32760, -8) == -32768);
}

static void test_interpolation(void)
{
    assert(audio_oracle_interpolate(123, -456, 0u) == 123);
    assert(audio_oracle_interpolate(0, -1, 1u) == -1);
    assert(audio_oracle_interpolate(-1, 0, 1u) == -1);
    assert(audio_oracle_interpolate(-32768, 32767, UINT32_MAX) == 32766);
    assert(audio_oracle_interpolate(32767, -32768, UINT32_MAX) == -32768);
    assert(audio_oracle_interpolate(1000, 2000, UINT32_C(0x80000000)) == 1500);
    assert(audio_oracle_interpolate(1000, 0, UINT32_C(0x80000000)) == 500);
}

int main(void)
{
    test_overdub();
    test_interpolation();
    return 0;
}
