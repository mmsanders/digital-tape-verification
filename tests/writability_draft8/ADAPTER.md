# Mechanical adapter contract

`wp06a_probe CASE_ID INPUT.vo08 OUTPUT.vo08`

Stdout one JSON object `WP06A-OBSERVATION-1`.

Device `write` is non-NULL. Media is structurally valid v1.1. Scripts:

- mount the named side
- `tape_get_info` (must report `writable==false`, `version_minor==1`)
- one mutator as named by the case
- unmount

Do not change fixtures or expected results to fit a product build.
