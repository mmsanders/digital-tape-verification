# WP-06h not-mounted assertion matrix

| ID | Assertion | Basis | Control |
|---|---|---|---|
| NM-A01 | Every ordinary call before mount is `NOT_MOUNTED` | Engine API §10 Not mounted; WP-06h | tell succeeded |
| NM-A02 | Every ordinary call after unmount is `NOT_MOUNTED` | Engine API §10; WP-06h | seek succeeded |
| NM-A03 | `tape_tell` leaves `*out_frame` untouched | Engine API §10; V5-009 | sentinel overwritten |
| NM-A04 | Zero writes/flushes | WP-06h | write mutation |

Ordinary calls: seek, set_rate, render, service, status, info, tell, arm,
feed, commit, abort, set_side, reset_b, promote, respool, dup-as-src, unmount.

Excluded: format/init/mount (permitted while not mounted), destination-side
dup, crash, continuation, listened PCM.
