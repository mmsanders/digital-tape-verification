# P1-R25 transport/warm retained product evidence

Verification-side retention for issue #40.

Authoritative final-head identities:
- Product commit: `dbd5a23291521cfe21da571fa97e14b806ace500`
- Workflow run: `35794299660`
- Transport job: `106969864466`
- Artifact: `p1-r25-transport-product-evidence` / ID `10723796203`
- Artifact ZIP SHA-256: `8226d421a6b6c2928f7107bfd01bd8a8233f3cfb331f6f88fdd46b16a02980ec`
- `observations.jsonl` SHA-256: `7fe8a9096ac57abd7ed62c22ace39b432de52801207f9ae396edf08ae57a7997`
- Original verifier publication: `5d97073ca03014e9d4055014f294709a78506b9e`
- Imported verifier tree: `05aafde29e3d8048bec669053b1bafcd0104cbd3`

The retained evidence file `observations.jsonl.zlib.b64` is a zlib-compressed,
base64 text encoding of the **exact** 29,395-byte artifact
`observations.jsonl`. Its compressed-byte SHA-256 is
`5e4a8df8f4f1af40eece3fde8325adff400ee1ff5b9c21f2b647881366db458d`.

`replay_product_evidence.py` decompresses the retained bytes, authenticates the
exact JSONL hash, ignores Software's stored verdict strings, reconstructs every
verifier fixture from the unchanged package, authenticates input/output hashes,
and reapplies `oracle.check` to the raw product call/callback observations.
