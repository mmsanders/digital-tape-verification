# Verification repository entry point

Read the Product repository's [CLAUDE.md](https://github.com/mmsanders/Digital-Tape/blob/main/CLAUDE.md),
[STATUS](https://github.com/mmsanders/Digital-Tape/blob/main/docs/STATUS.md) and
[Verification charter](https://github.com/mmsanders/Digital-Tape/blob/main/docs/ROLES/verification.md),
then the task Michael gave you. This file grants no role or assignment.

**Scope since 16 November 2026 (Product ADR-210).** Independent, tests-first verification
is used for changes to the engine, the frozen spec and the goldens, and for reviews
Michael asks for. Firmware, desktop-tool, hardware and tooling work no longer comes here
as a matter of course. With no engine or format change proposed, this repository is
normally idle.

Everything published here is immutable: never change old package bytes to update status.
Publish a new package instead. Navigation: [CAPABILITY-STATUS](CAPABILITY-STATUS.md),
[tests](tests/README.md), [findings](findings/README.md). Historical plans and PM copies
are provenance, not work directions.
