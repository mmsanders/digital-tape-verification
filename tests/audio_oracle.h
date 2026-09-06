#ifndef AUDIO_ORACLE_H
#define AUDIO_ORACLE_H

#include <stdint.h>

int16_t audio_oracle_overdub(int16_t existing, int16_t input);
int16_t audio_oracle_interpolate(int16_t a, int16_t b, uint32_t phase);

#endif
