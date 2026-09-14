# P1-R13-V — per-render scrub service correction

**Disposition:** Ready for PM review. `P1-R12-V01` is cured in the verifier-owned
package only. This return accepts no product observation, implementation, adapter,
complete WP-08, PCM, WP-11 golden, listening result, merge, or held work.

## Identity and boundary

- Assigned verifier parent: `bc0f7ec6ba05a1e7bb7033d99922e7b739abd10d`
- Source commit/tree, created before evidence: `1f7fe3f79d326c4a6e37f8c301c97c110d481619` / `fe79113bfe600268585b382fab218e2bbf687a7e`
- Evidence commit/tree: `05e193209542d204669b32f485dad21007a084ee` / `006d1a0875797d05bf7d137652ac97209c16c4ef`
- Corrected complete-package tree at the evidence commit: `467a34bb0a84672c5bdef9059f2dd326d6435eb6`
- Synthetic evidence tree: `3323542c187f4121beddb3c8960ed2e35992e586`
- Frozen WP-08 SHA-256: `ff519e960ed3db6e401baebd12f33d5527f83f0e4dfec12484f498470198a96a`
- Frozen TapeFS / Engine API / acceptance SHA-256: `3bffa0ec46d7ba3779b02cbee6fac1edaf5094553f78270ee379759655147cbb` / `537eadc423e1a7bde726d689206b8fe93bef164d57e48e8ff71e07eaf8a7e3a1` / `7f78fba7b66b4fc6e96d15399c62468249bb30fbccbb59bf9f57b4532f56b6b7`

No product implementation, firmware, product adapter/probe, private Software test,
or PR #77/#64/#20 diff or discussion was inspected or run.

## Correction and controls

The scrub oracle now requires a finite `tape_service(block_budget == 1024)` sequence
ending with `more_work == false` immediately before every render request. The
synthetic public-contract model emits that schedule independently for every one of
698 renders in each direction (698 service completions, 16 rate calls per direction).

Two named controls reconstruct the rejected once-per-row schedule independently:

- `P1-R13-V01 old once-per-row cadence forward` — caught
- `P1-R13-V01 old once-per-row cadence reverse` — caught

The complete-package self-test passes ten families and 22 behavioral controls,
including the two cadence controls and F-1/F-2/F-3. The retained P1-R4 package and
all 18 of its controls remain mandatory and pass. Evidence identity, relabel,
tamper, exit, timeout, nonempty-destination and offline-replay controls also pass.

## Source changed-file inventory

All source changes are mode `100644`.

| Path | Git blob | SHA-256 |
|---|---|---|
| `tests/playback_complete_draft8/COVERAGE.md` | `7cf313b55f94db2f6a54dbdc9a68c8eb22657da7` | `a496840323a5937b79e9b908c63dba9808c6e01cb1ba844d4239b891988ef564` |
| `tests/playback_complete_draft8/README.md` | `b874d6c7004e80021b1542965b8e2223f34b2802` | `d397ab1ef4e206a265cb936c5ecf4cc88c8978b18b04186736d396b69680724b` |
| `tests/playback_complete_draft8/_synthetic_adapter.py` | `eda53cffbd4d8d95fb069c05e4df5a1542abfa02` | `75d3ba58550fd2d46114d5dd0048f77cd29ed795668bec5bfad81563fc3f84e3` |
| `tests/playback_complete_draft8/oracle.py` | `86aa77f8acaac6ef98de2e14c15a025fb987ffd9` | `0e8161c962c496c0d84c79a71473188a793e09aa08c3eb6630400f76447da7e6` |
| `tests/playback_complete_draft8/package.json` | `111fa007c99b377c466e5a09e771e2a76f8412ae` | `b9ec085565e8481084dc8c287082cf69cc3419f938a7fe89a08b98ec9904b0c4` |
| `tests/playback_complete_draft8/replay.py` | `5000076a310a1cac3df344743460d572d619bc09` | `d5609378a4ed1769287ec727129bc8ec821df27eff19d0fbc72b8fd9cab366f1` |
| `tests/playback_complete_draft8/runner.py` | `4f54f675aaf883f96319286194769835ae691b42` | `1b4ca3c2014df70ca1cde6f8d88932aaa7cad42402f57aa50943afba070bf689` |
| `tests/playback_complete_draft8/selftest.py` | `1f55dcc0dce291b4bca464968d0dd4586ecd727b` | `cce017f006fd0484b227683801da946e51e3e08685079efa0aed5a6ae349a6cd` |

The evidence commit adds exactly 32 files: the retained cadence-control log plus the
31-file `p1-r13-synthetic` tree. Every file except `manifest.json` is path/SHA-256
bound by its 30-entry `files` inventory. The remaining exact identities are:

| Path | Mode | Git blob | SHA-256 |
|---|---:|---|---|
| `tests/playback_complete_draft8/evidence/p1-r13-cadence-controls.log` | `100644` | `4905dc1227fe9503e8da1cd1b9e86684ef66716b` | `86f9f8274f6dcedb2bfc769be25c864e0ce153e628b83692eb878a24c70b5032` |
| `tests/playback_complete_draft8/evidence/p1-r13-synthetic/manifest.json` | `100644` | `34ae95265be492ae8da971c63c9af7e78ddc1ac1` | `94f17383b944d510094a57791c1601fb029d97655874ed7a90eefaf721bf1f05` |
| `tests/playback_complete_draft8/evidence/p1-r13-synthetic/output/observation.json` | `100644` | `9778d314dc404429b478c815a3c2b7d1329418fc` | `a7c00a87708103f968c723adc80478934d81374134f682b4fbc5638187d170ec` |
| `tests/playback_complete_draft8/evidence/p1-r13-synthetic/result.json` | `100644` | `ced59153ef47102ddf7d993fe234bcdd9ad68601` | `1fb3437a3fffb668ce92e3e6391f4d06d1ead07b8b24889a0264c9fe0d75f742` |

The immutable evidence commit/tree plus manifest constitute the exact complete
mode/blob/SHA-256 inventory; `generate_fixture.py` is the sole `100755` evidence
payload and all other evidence paths are `100644`.

## Reproduction and results

Run from repository root unless a `cd` is shown:

```sh
cd tests/playback_complete_draft8
python3 generate_fixture.py
python3 selftest.py
python3 runner.py --adapter-cmd 'python3 _synthetic_adapter.py' --adapter-kind synthetic --adapter-id verifier-p1-r13-per-render-service-model-v1 --adapter-source _synthetic_adapter.py --adapter-build 'python3 source; verifier P1-R13 synthetic public-contract model' --adapter-timeout-seconds 90 --source-commit 1f7fe3f79d326c4a6e37f8c301c97c110d481619 --source-tree fe79113bfe600268585b382fab218e2bbf687a7e --evidence-dir evidence/p1-r13-synthetic
python3 replay.py evidence/p1-r13-synthetic
cd ../..
make -C tests check
```

Results: deterministic generation passed without writes; both candidate PCM hashes
remain `41e882e...` / `5f1794e...`; the source self-test passed; the evidence run and
offline replay passed; and the full verifier suite passed after checked-in evidence.

## Holds and next owner

`P1-R12-V01` is resolved only for verifier-package correctness. Candidate PCM is
synthetic, unlistened and unaccepted. The narrow P1-R12 mount-observation disposition
is unchanged. PR #77 remains draft/held pending exact mechanical re-import, a fresh
Software trace, PM authentication and a new independent Verification disposition;
PR #64 and #20 remain held. Allocator, recording, crash/recovery, warm-start negatives,
state/operations, performance, hardware/cards, purchases, fabrication, charging and
safety remain excluded and held. Next owner is PM.
