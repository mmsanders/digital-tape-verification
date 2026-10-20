# Verification223 — ADR190 distinct-disk supplemental proof controls

20 October 2026. Product authority6130c8f826e3586dab149e3d4484edb18c04689a, WP14-NATIVE-CAPTURE §2.5. Current local input Product5c17314af51ac22e8729d474f2a4d2edd756daef; Verification929c02f35aed6bad05d708d33ebff0cfb35ccc37. Live223 updated2026-10-20T15:41:51Z, following208's bounded S2 completion. No subworkers.

This first publication authors a **sufficient proof route**, before applying it to the complete retained physical capture. It does not change the accepted checker, issue an A6 PASS, or claim this is the only permissible native correlation method. The existing old-checker FAIL remains immutable. An alternative native request/offset-space bridge could be valid only with its own positive raw evidence and independent detecting controls; no bridge or equivalence is inferred from a filename, proximity, key and size alone.

The supplement requires complete captured base binding, no trace loss, successful full final-sector return and no target writes/flushes or other failures. A FileIo exclusion needs a unique nonzero key and request binding to one explicit other-disk write, agreeing byte count, known matching offset coordinate, request time and no conflicting/reused key evidence. DiskIo identity must be explicit. Every remaining record must be proved once; target-disk/different-stream writes, unknown identity, unmatched post-exit reads and ambiguous matches remain non-PASS.

**Controls:** one positive native-fact model plus20 causal negatives: target/missing disk, missing/different key, length/request mismatch, duplicate counterpart, key reuse/ambiguous life, same-card other stream, post-exit target read/write, missing/short completion, lost events/buffers, offset mismatch/unknown coordinate, time inversion, unknown native identity and other old-checker failure. These are independent synthetic proof-model controls, not real traces, reader tests or Product behavior.

Normal physical-evidence CI carries the16 unchanged accepted-checker controls and existing compact fact checks, then executes these21 new supplement controls. Full private capture application follows only after this control publication is merged. No private trace, binary or personal path is published in this control package. No physical rerun, security change or Product implementation work is authorized by it.

## Retained-complete-capture disposition

**Old accepted checker: FAIL, reproduced unchanged. Separate ADR190 supplement: HELD; zero records excluded.** Control publication PR228 was merged at `b0eddaaab3fa32e8902fa7fe93446983c29025fa` after CI39455159853 SUCCESS before this application. One private local replay authenticated the original92,802,476-byte ZIP SHA2560246c24a96b1de22bad15086aa925def9d2b43bb6ecd13c146a305f914df0bcb, all29 member hashes and exact accepted checker SHA2567cbba051629d56bffd85e715fe34cb909421aa6b105a52c883f383aed10b8d89, then reproduced the original complete CHECKER-RESULT byte-for-JSON-value. No Windows binary was executed.

A separate independent XML identity scan authenticated SHA25669a81ab6ca7f8aaf7d533b511c496c048bd4c11620999e0159d5898c6fe4ff98 and streamed **948,634 original records**. It found129 FileIo writes and129 DiskIo writes using the disputed log key, with one distinct key name. Both selected DiskIo writes explicitly name disk0, distinct from target1; this remains a useful positive disk fact but does not by itself bind each FileIo request.

| FileIo / DiskIo records | FileIo IRP | DiskIo IRP | File offset / disk offset | Bytes | Same-key/size DiskIo candidates in full trace |
|---|---|---|---|---:|---:|
|480422 /480439|0xffffa18627895918|0xffffa1861c4eb010|16384 /3261186048|4096|69|
|480466 /480483|0xffffa1863e7e99d8|0xffffa1861c4eb010|81920 /3261251584|8192|25|

Each FileIo request has **zero** matching-request/same-size DiskIo writes under this key. Both offsets have a constant observed delta3261169664, but that is not an independently established file-extent/offset-space translation. No record contains both one of these FileIo request pointers and the selected DiskIo request pointer in named fields or raw payload. This is a bounded pointer-link scan, not an assertion that every other provider schema has been independently decoded or that no possible alternative method can ever work. No complete native bridge is established by this review.

**Precise blocker:** the captured key, size and nearby timestamps support a plausible correspondence, but the available differing request identities and offset spaces lack the positive independent bridge required for this exclusion route. Key naming is stable but key/length alone is non-unique over the complete capture. No FileIo record is exempted on a filename, thread exit or inferred correspondence. No new A6 PASS is issued. The old result's two complete512-byte last-sector returns, zero observed target writes and no-loss facts carry exactly, without overriding its four-record failure.

**Next owner: PM476/479.** Preserve the no-new-capture instruction. A different issued sufficient proof route must explicitly establish the native upper/lower request or extent translation with detecting controls, or this capability remains HELD. The existing result does not establish card failure and does not authorize another capture, new tool, weaker criterion or Product checker change. Mac/fullWP14/write/media/atomicity/target timing remain separate.

Replay privately after authenticating the original ZIP and checker with the unchanged prior `P2-A6-PHYSICAL-2026-10-19/replay.py`, then run:

```sh
python3 -B findings/P2-223-METHOD-2026-10-20/scan.py ORIGINAL/verify.xml --out private-result.json
```

Compare the bounded public RESULT.json. CI replays21 proof-model controls,16 unchanged accepted-checker controls and validates bounded fact/result consistency; the full original ZIP/XML replay is **local only**, not CI. Raw full-machine evidence remains private. Close223 at this precise blocker and continue226 as issued; no physical retry or Software wake.
