# WP-17 witnessed bench record (not executed)

Record exact firmware commit/binary SHA-256, engine tree, toolchain/core versions,
board/codec revision, card part/capacity/revision/CID, supply, audio setup and witness.
Follow FW-1's fixed-low-output volume check before wearing headphones.

1. F1: prepare the seven normal-rate WP-11 manifest cartridges with the pinned
   desktop executable. Render the same side, start position and frame count at
   44.1 kHz, signed 16-bit stereo 1x. Capture raw PCM before codec conversion.
   Retain capture bytes/hashes and `wp17.py pcm` results for every case. Flip one
   captured sample and require rejection. Scrub vectors are separately identified.
2. F2: retain target linker map, measured instance bytes and section accounting.
   Paint the actual stack, exercise mount/service/render/Stop/removal paths, retain
   high-water bytes and margin. Budget ≤8192 bytes; missing measurement stays pending.
   Compile an oversized-static build and require the resource gate to fail.
3. F3: mounted cartridge, sleep then wake; record wake GPIO and decoded I²S channels
   with a logic analyser. First non-silent frame minus wake edge must be <100 ms.
   Record sample/edge resolution and uncertainty; a result whose upper uncertainty
   bound reaches 100 ms cannot pass. A deliberately delayed control ≥100 ms must
   fail. Firmware timestamps alone do not accept F3. Retain all trials, including misses.
4. F5: Play from a known nonzero position, record PCM and public position. Stop,
   wait, show no rendering/position advance, Play again and compare continuity.
   Pull the cartridge during playback; retain stopped-audio observation and clean
   unmount result when possible. Reinsert off-device and retain `tapectl verify`
   output/exit and card hashes. No-write playback must not change card bytes.
   A deliberately continuing-render/position-drift observation must fail the check.

F4 waits for WP-18/19 recording. No target criterion is passed by this checklist.
