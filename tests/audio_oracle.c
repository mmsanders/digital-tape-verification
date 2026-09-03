#include "audio_oracle.h"

#include <stdint.h>

int16_t audio_oracle_overdub(int16_t existing, int16_t input)
{
    int32_t sum = (int32_t)existing + (int32_t)input;

    if (sum > 32767) {
        sum = 32767;
    }
    if (sum < -32768) {
        sum = -32768;
    }
    return (int16_t)sum;
}

int16_t audio_oracle_interpolate(int16_t a, int16_t b, uint32_t phase)
{
    const int64_t denominator = INT64_C(4294967296);
    int64_t product = (int64_t)((int32_t)b - (int32_t)a) *
                      (int64_t)phase;
    int64_t quotient = product / denominator;
    int64_t remainder = product % denominator;
    int64_t value;

    /* C99 division truncates toward zero. DRAFT-4 requires floor. */
    if (product < 0 && remainder != 0) {
        --quotient;
    }
    value = (int64_t)a + quotient;
    return (int16_t)value;
}
