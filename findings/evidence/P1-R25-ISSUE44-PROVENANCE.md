# Issue #44 evidence identities

## Corrected promote

- Product head: `262db463680798c63fde8b18232e60bdbda15f0a`
- Workflow run/job: `35822408762` / `107056879078`
- Artifact ID: `10733633872`
- Artifact ZIP SHA-256: `fc34a1c02e3aae0ad752a5df19a633605befcf0776b8c3ea8cea442f86763c6b`
- Manifest SHA-256: `881fdaf684dd26742f126649976088f79fabba1f4457d37f0f7b52ff6f17cad6`
- result.json SHA-256: `0adac30b74b7de59d012b7a86afe3f87f22755d86a4cc794b8549f37a8f2eaa7`
- Deterministic observation-set SHA-256: `83c8475b1f1a507a8118b06fd5b040fb09c4b9465c12a5826fb75eff4704023e`
- Corrected adapter source SHA-256: `2371430e4e4e40d8e7349cd38bdcf050749f1756e14cab378ae3b301b267eb7f`
- Unchanged oracle SHA-256: `b9ef4b3098869e50d9ed8639578726c395c51cd8b419e877f2af58ada712c78f`
- Verifier publication/tree: `e5e06b06f1aa0755a3b0b15133f1ce680e17f7af` / `2b79e0b07016da3521917c5a276e36994ccccfa6`

The observation-set digest was independently reproduced from the downloaded
artifact as SHA-256 over sorted records encoded as
`CASE_ID + NUL + SHA256(observation.json) + LF`.

## Common-head respool

- Product head: `262db463680798c63fde8b18232e60bdbda15f0a`
- Workflow run/job: `35822408762` / `107056879100`
- Artifact ID: `10733568919`
- Artifact ZIP SHA-256: `8cb54b51b66356e089be6c7a54f86006d0454c330458855f54c638e3c84f77e4`
- observations.jsonl SHA-256: `5db21452b759b2f113508d6731ae90ac99bcf80e5c8a223ae521009d1d30c81c`
- PROVENANCE.md SHA-256: `7d7b2d58e60c353be01ae9f7c4f38d3c43edcdda1ce442936be3819ef5b7ab10`
- Adapter source SHA-256: `a5ac8d8fbdc0fa5a1e85ba7f8f26a0396b67fc469b72ede3f94de9283c22b904`
- Verifier publication/tree: `6519220f161254c0453a30858eb3e7073e2eb82b` / `caf607917240c5a96fd32f526ee8e2a4761ebb24`

The Actions artifacts remain the authoritative retained raw evidence. This file
binds the Verification return to their exact bytes; it does not replace them.
