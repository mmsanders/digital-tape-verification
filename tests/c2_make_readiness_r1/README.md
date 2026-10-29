# C2 Make-readiness supersession — Verification370 Stage A

APP-1 §2/§4 as amended by ADR-195 governs current Make readiness. It is enabled
only with one offered card, a valid nonempty label, a successful current music
check, retained audio and no check/Make/confirmation running. Discovery by itself
does not enable or authorize Make. Existing label/child/error/safety tests carry.

**Superseded global wording:** `windows_discovery_r1/README.md`'s “permanently false
Make” and “Hard hold”, plus `windows_interactions_r1/README.md`'s “permanently
disabled Make”, describe the earlier S2 tranche only. They impose no permanent
restriction on the current app. r2's inherited false assertions have the same scope.

The immutable discovery/interaction validators and their negative controls remain
valid for their existing **no-retained-audio fixtures**, not for the fully ready
Make state. In particular:

| Old assertion | Current bounded meaning |
|---|---|
| Discovery `expected(...).make_enabled=False` | Card discovery results alone do not supply retained checked audio. |
| `valid_music_label_one_hint_make_enabled=False` | The legacy typed success/label/card fixture has no retained artifact; it is not the complete current readiness precondition. |
| r1/r2 interaction snapshots and r2 summary require false | Their controlled completion supplies outcome metadata without retaining an actual audio job. Editing/poll/details checks do not authorize Make. |
| No make/elevation calls in discovery/interaction capture | Those tests perform no Make action. This does not prohibit the separately tested confirmation/Make route. |

No old package bytes, case expectations, summary indexes or assertion values are
rewritten. Product's existing CI calls remain legitimate for those bounded inputs;
they cannot be cited as a universal “Make must be disabled” gate. All unrelated
parser/nonce/discovery/single-flight/selection/editing/details/cleanup controls
remain required. No Product edit, candidate rebuild or re-clearance is needed.

`contract.py --emit` independently issues72 combinations of card count, label,
check result, retained-artifact fact and idle/confirm/making state. `bridge.rs`
captures actual production Bridge snapshots in a disposable checkout; the Python
qualifier owns the expected outcomes. There is one positive fully ready row and71
negative rows. Always-disabled and always-enabled controls are rejected, as is an
inversion of any row. Artifact availability and terminal child outcome are typed
unit inputs; this test launches no child or native app, opens no device and proves
no physical/native acceptance. Existing C1 real-child retention/Make evidence carries.

Run `python -B tests/c2_make_readiness_r1/contract.py` for oracle controls, or pass
`--input ROWS.json` to qualify actual captured rows and run the same negative controls.
The hosted workflow pins Product main1d341573, whose app is the already-cleared
5101e3f3 app. G1/G3/G4/G5 remain pending Michael's C2 return on Product628; G2 is later.
