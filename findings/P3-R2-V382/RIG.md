# V382 — R374-1 result and ready timing bindings

Exact Hardware PR646 head2faa1180c6f12eb4598d1f25351766f550064055, based on
Productcc23b87f, reviewed under V382/ADR204 at Product51d0f8f. Engine/firmware scope
is unchanged; the return's diff against its base is confined to hardware/.

**R374-1 corrected aggregation: PASS in the published bounded scope.** The existing
27-case independent suite runs against exact judge blob
8086e3598783441a06d547368d01d5baafe6956c, SHA256
6824e0048135ad2096e872f040a655117b1d6206a8567de020625fbe33728691.
All27 pass, both actual candidate mutations and six predicate controls detect.
The independent Windows execution from Michael's preceding review is carried in
R374-1-WINDOWS.json; Linux CI executes the same bounded suite for this publication.
No broad accepted campaign is repeated. This is not clearance of the whole PR.

Authenticated import:9f611c4 is an ancestor of judge-change dc38a4d. Its changed
paths are solely the import manifest and unchanged verifier package; imported tree
1ca703a44cdffc940201068b24b9ad8673fee644 exactly matches V380 before implementation.
The covered implementation diff classifies every validated row and all four
neighbours before final verdict, while qualifying count remains separate. No
uncovered timing implementation was opened to derive expectations.

**New row binding:** tests/rig_timing_r1 has71 executable declared-model cases and
seven predicate controls. Self-test only; new qualifier implementation absent.
Model U1us and delay500us do not become calibrated physical limits through a test.
The README lists the precise remaining manifest/plan/rollback interface dependency.
Hardware must load and authenticate the actual manifest/control contents, not just
compare hash-shaped row fields. Edge direction/chatter/chronology consistency and
ADR204's strict rollback/equality rules need an explicit corrected declaration.

**Rig method remains NOT CLEARED.** Circuit changes withdraw the old unsupported
LVC threshold and discrete FET dead-time claims, but new figures remain analysis.
The TLV3202 datasheet55ns switching bound has specified overdrive/load conditions;
it does not alone establish the rig's slow-rail crossing delay budget. E3's shared
GPIO edge is not the slow-A/fast-B waveform pair. Review/calibrate those relevant
conditions before accepting U. Primary source, sections6.6/6.8:
https://www.ti.com/lit/ds/symlink/tlv3202.pdf . No measured violation is claimed.
The reference-current assumptions for the selected2.048V LM4040 row and complete
board supply/loading/transition bounds also remain to be confirmed; E0–E3 and
all dry-run controls remain unmeasured, not substituted by these synthetic rows.

R374-5 stays SPI-only characterization. No card, native SD4/SDR50, physical campaign,
purchase, safety/acoustic or fabrication/charging clearance. Product merge stays
with Software/PM routing; this publication merges no Hardware implementation.
