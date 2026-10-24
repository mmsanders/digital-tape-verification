# P2-305-001 — actual progress state masked by adapter metadata

Verification305 correction1,24October2026 UTC, under PM561. Inputs Product main
db0325a9befa333cbc128b24bd2ef3690c48ac08 / Verification main
9f6f9dba46d09474615bf8f03b574f9a72c09d80. Canonical four/live305–307/562–564/
PM561 read;305 updated02:28:04Z. Started partial review3056378781855 of offered
progress packet3056378750859 /5626378750192. This is NOT a final Ready/Blocked
return or integration clearance. No issue is reopened or closed by this correction.

Covered candidate is draft566 head0c95c45f818fd80836b10ed13fcf443bc4e1c216,
renderer/adapter sourcec7c6a4a16befcc69923f9fde621aa7c425613411. Independent305
publication3395377d5abf37ff32b9b796b492db15664077c7 subtree is exactly imported
at391c0cb9686f0d2f56e12aebfbdb01f72bbc8758 BEFORE implementationb83166e.
Docs-only head leaves renderer/adapter source unchanged. Runtime module SHA256
1bef0045be9a6468199c805e48d74acd716e95263a4078778a7dc67d50266283 matches Git.

## Finding, priority2

In host/app/frontend/screen.mjs render(), a Problem with unknown length removes
the progress value attribute but keeps the progress element visible (only Done
sets hidden). It separately labels data-indeterminate=false because the state is
not Checking. tools/app/screen-dom.cjs capture() reports that data flag as the
observed indeterminate fact, instead of reading the actual browser control state.
The frozen305 predicates require false in these terminal unknown-length views.
The adapter therefore reports a pass while the retained control is indeterminate.

Original screen-run3 DOM and observation bytes independently authenticate SIX
cases: folders-only, protected, unusable, folder-content, generic and escaped-name.
Each retains the same relevant markup:

`<progress id="length" max="1" data-kind="length" data-too-long="false" data-indeterminate="false"></progress>`

There is no value or hidden attribute and no applicable CSS rule that hides it.
HTML's native progress state is indeterminate when value is absent; a renderer's
data attribute does not change it. The [HTML Standard, progress element](https://html.spec.whatwg.org/multipage/form-elements.html#the-progress-element)
defines absent value as indeterminate and position=-1. This is a test-DOM/source
finding, not observation of the actual Windows Digital Tape UI.

Exact retained DOM SHA256
83124d080bf223521cac84a5197e942148ee4c0ebe576fac9bbfb4db199a5fee;
observations SHA256
7230d79abe34149f09326f5ea56b32457e18eaa986a6f236751be96afd6efe00.
audit.py/RESULT.json authenticate original Git/module/import/DOM facts read-only;
no Product, browser or accepted actual experiment was replayed.

## One consolidated exact-delta response

Correct the renderer's terminal unknown-length presentation and measure actual
DOM/control state in the test adapter (for example native position/:indeterminate
plus actual visibility). Do not derive observations from the renderer's declarative
data flag alone or relax the frozen false expectation to fit it. Preserve Checking's
indeterminate state, all exact ratio/overage/copy/label/details and disabled routes.
Demonstrate the faulty visible/no-value/data=false combination is detected by the
actual observation/unchanged expectation; changed source/adapter test-DOM captures
must identify exact bytes. This is an observation-binding correction under already
published305 expectations, not a new native/UI test/provider or new product state.
No unchanged accepted/failed experiment should be replayed merely for this review.

No other covered renderer miss found in this bounded source pass. It uses plain
textContent/value, rejects whole over-byte/NUL/unpaired-surrogate labels, forwards
whole path batches, leaves Make disabled without an action, and offers selectable
plain pre details. The earlier producer textarea CRLF correction is retained, not
counted as an independent correction round.14-view claim is not accepted as stated
because six indeterminate observations are masked.8 label and other raw observations
remain inputs, not blanket acceptance. Current source CI is not a UI/renderer test:
four workflows green and engine queued at this review snapshot; normal current-base
gates remain required. No Product merge was performed by Verification.

Producer explicitly leaves combined actual host admission/reset/copy rows unexecuted;
that temporary306 dependency is truthful. Literal View.message/details fixtures in
the current adapter establish renderer projection only, not authoritative backend
message selection. Full305 qualifier, new disabled-discovery fixture and actual
composed host rows remain pending. index.html has no bootstrap yet by declared563
scope, so it is not an assembled page or GUI clearance. No untested host source was
inspected, no original backend/parser/real-child/native/window test was repeated.

Next owner Software562: one consolidated exact-delta correction, then return ready
covered source/evidence under normal CI; shared rows can complete with563.305 stays
OPEN while issued305/306/307 work remains. No cards/discovery/Make/elevation, native
UI298/session/A6/INGEST/fullAPP/S3/G2/physical clearance. Quarantined pre302 history
and old STOPs remain explicit, with no reuse or retrospective certification.
