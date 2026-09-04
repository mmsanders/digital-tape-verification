#include "audio_oracle.h"

#include <assert.h>
#include <stdint.h>

static int16_t portable_shift_interpolate(int16_t a, int16_t b, uint32_t phase)
{
    int64_t d = ((int64_t)b - (int64_t)a) * (int64_t)phase;
    int64_t q;

    if (d >= 0) {
        q = (int64_t)((uint64_t)d >> 32);
    } else {
        uint64_t magnitude = (uint64_t)(-d);
        q = -(int64_t)((magnitude + UINT64_C(0xFFFFFFFF)) >> 32);
    }
    return (int16_t)((int32_t)a + (int32_t)q);
}

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

static void test_all_deltas_at_boundary_phases(void)
{
    static const uint32_t phases[] = {
        0u,
        1u,
        UINT32_C(0x7FFFFFFF),
        UINT32_C(0x80000000),
        UINT32_MAX
    };
    int32_t delta;
    unsigned int phase_index;

    for (delta = -65535; delta <= 65535; ++delta) {
        int32_t a32 = delta < 0 ? 32767 : -32768;
        int32_t b32 = a32 + delta;
        int16_t a = (int16_t)a32;
        int16_t b = (int16_t)b32;

        for (phase_index = 0;
             phase_index < sizeof(phases) / sizeof(phases[0]);
             ++phase_index) {
            assert(audio_oracle_interpolate(a, b, phases[phase_index]) ==
                   portable_shift_interpolate(a, b, phases[phase_index]));
        }
    }
}

int main(void)
{
    test_overdub();
    test_interpolation();
    test_all_deltas_at_boundary_phases();
    return 0;
}
