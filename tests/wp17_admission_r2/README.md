# FW-1 admission correction, revision 2 — Verification378

Authority: ADR-202 / Product PM648, issued in Product merge
`b07d8d4832fb6c4213efa950d47e827c34e6ea65`, and live Verification #378.
Exact unchanged Software head: `ee478a913613a16a90e38c85112fb67cbbf53887`.
[AUTHORITY.json](AUTHORITY.json) pins the decision documents and every carried
file's predecessor identity. Prior `p3_r1_r374`, `wp17_candidate_r1`, original
reports and evidence remain byte-unchanged.

This is an explicitly authorized new expectation, not an assertion adjusted to
fit firmware. Admission checks bytes 446–511 (signature and all partition-table
fields, extents and bounds) under WP-14 §2/E-1. Bootstrap bytes 0–439, disk
signature 440–443 and reserved bytes 444–445 alone do not refuse admission.
Full WP-14 §4.1 validation is separate: desktop verify still diagnoses bootstrap
and reserved-prefix defects on these admitted fixtures, while disk-signature
variation alone is not that finding.

Run on the exact candidate's normal host build:

```
python3 tests/wp17_admission_r2/check.py --product PRODUCT --fwhost PRODUCT/build/fwhost/fwhost --tapectl PRODUCT/build/host/tapectl --out RESULTS
```

Twenty-eight cases cover nine admitted layouts (clean, first/last/all bootstrap,
disk signature, either/both reserved bytes and combined prefix) and nineteen
refusals (both signature bytes, statuses, CHS/type/start/count fields, extra
partitions and zero/overflow/past-card extents). Each accepted view returns exact
first/last P2 bytes, performs one legal translated write and refuses before/after
view I/O; the entire remaining image must be unchanged. Every refused card stays
byte-identical. Desktop diagnostics run on pristine copies before view writes.

Four causal controls use actual returned observations: blanket acceptance,
wrong reported offset, a raw image actually modified outside P2 despite correct
reported metadata, and false bounds handling must all be rejected. No Product
source or physical disk is modified for these controls.

The run authenticates exact source trees, predecessor ancestry and carried-file
hashes. It confirms seven retained normal-rate PCM payload digests against the
unchanged WAV data and separately authenticates the whole-WAV file digests.
That is offline identity checking, not another golden/render/fault campaign.
F1 host/F2 static/F6 and prior Stage A/rig results carry from their exact merged
publications. Only admission/view/desktop-diagnostic cases execute anew.

Clearance is limited to unchanged ee478a91's authorized off-target integration
scope, with Software #642's required current-base CI still required. Target F1
PCM/I²S, actual instance/stack measurements, timing, physical controls/removal,
all safety/media/physical holds, rig NOT CLEARED, and batching limitations stand.
