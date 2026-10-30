# C2 polling usability confirmation

29 October2026 PDT. Michael directly continued the C2 review after publication
`12187bb8b534a059bbbb93439d405c72fcc06946`. This addendum supersedes only that
disposition's unconfirmed native label/details polling observation. Original
disposition, packets, audit and candidate bytes remain unchanged.

Verification supplied this short non-writing observation check on the same app:

1. With the card inserted, type `C2 LABEL CHECK`, place the caret between LABEL
   and CHECK, wait6seconds, then type X. Also type slowly across several polls.
   Expect insertion at the selected position without lost characters or jumping.
2. Drop the nonmusic folder, open Show details, select diagnostic text, wait6seconds,
   copy and paste it into Notepad. Expect the panel and selection to persist, the
   copied text to match, and the nonmusic error to remain through polling.

Michael returned:

> 1. The cursor does go away but doesn't move when I type. No flashing or jumping. text appears in the right spot.
> 2. pass

**Label polling usability PASS; details polling usability PASS**, under ADR-195's
human-observation evidence standard. The caret's temporary disappearance alone is
not a failing observation: the reported insertion position remained correct,
with no jumping. Normal caret blinking is a plausible explanation, not an
independently measured mechanism. No new screenshot or trace is required to
accept the returned outcomes. No new Make/pull/verify or device write was requested.

Michael separately confirms: "The single-song rejection gap is real."
**F370-1 remains OPEN:** the rejected-file notice lacks Show details. PM owns its
explicit contract disposition or bounded Software correction. That is now the
only remaining item from this C2 review; the native polling observation gap is
closed. G1/G5, required G3 outcomes, no-lists/four-state screens and the real
cartridge byte checks carry unchanged. Complete APP-1 presentation/G2 clearance
remains held on F370-1. Verification370 stays closed at its completed return stop.
