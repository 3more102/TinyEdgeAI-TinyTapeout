# TTSKY26d Submission Checklist

Verified: 2026-10-01

This checklist separates **silicon readiness** from the external Tiny Tapeout submission step. A passing repository is not considered submitted until a revision is accepted in the Tiny Tapeout submission portal.

## Target shuttle

- Shuttle: **TTSKY26d**
- Process/flow: SKY130 / Tiny Tapeout `ttsky26d`
- Official closing date: **2026-11-30**
- Project size: **1x1**
- Top module: `tt_um_3more102_tinyedgeai`
- Clock: **40 MHz**

Official references:

- Shuttle schedule: https://tinytapeout.com/chips/
- Submission guide: https://www.tinytapeout.com/guides/advanced-workshop/submit-your-design/
- Submission portal: https://app.tinytapeout.com/projects/create
- SKY Verilog template: https://github.com/TinyTapeout/ttsky-verilog-template

## Frozen silicon candidate

- Final PR head: `f5f9bddeb6662d3eb89059fabe67a3e48a625b6b`
- Verified PR merge tree: `913eaaaa68e7c52f0c90a3398c76a4928a73a45c`
- Actual merge commit: `b46c1581f383f8154c74109b662be0c51d7162d1`
- Current post-merge documentation head before this checklist: `d7aa270db0ec7e4ed8e8fdffed6ea5af006c7bbb`

The two commits between the actual merge commit and the post-merge documentation head modify only `README.md` and `docs/SILICON_SIGNOFF.md`. They do not modify RTL, `src/config.json`, `info.yaml`, pin mapping, or physical-flow inputs.

## Repository gates

- [x] `info.yaml` uses `yaml_version: 6`
- [x] Top module begins with `tt_um_` and matches RTL
- [x] `source_files` lists both RTL source files
- [x] `test/Makefile` source list matches the project RTL
- [x] Complete 8-bit input/output/bidirectional pin documentation
- [x] `docs/info.md` explains operation and testing
- [x] Apache-2.0 license present
- [x] RTL/model regression passes
- [x] GDS build passes
- [x] Tiny Tapeout precheck passes
- [x] Gate-level regression passes
- [x] DRC passes
- [x] LVS passes
- [x] Setup and hold timing pass at the 40 MHz target
- [x] Antenna checks pass

## Latest post-merge CI

For `main` commit `d7aa270db0ec7e4ed8e8fdffed6ea5af006c7bbb`:

- [x] test workflow run #32 — PASS
- [x] docs workflow run #32 — PASS
- [x] gds workflow run #32 — PASS

## External submission steps

These are intentionally not marked complete unless confirmed by the Tiny Tapeout portal.

- [ ] Create/import the project in the Tiny Tapeout submission portal
- [ ] Select **TTSKY26d**
- [ ] Complete the order/coupon/payment step as applicable
- [ ] Press **Submit Project**
- [ ] Press **Submit a new revision** for the exact repository revision
- [ ] Confirm the submitted revision is associated with the intended Git commit
- [ ] Record the portal project/revision identifier in this file
- [ ] Re-check the portal after any repository change that affects the submitted revision

Tiny Tapeout's current submission guide explicitly requires submitting a **specific revision** after project creation. A project entry alone is not the final tapeout submission.

## Change-control rule

Any future change to RTL, `src/config.json`, `info.yaml`, the pin mapping, source-file list, or physical-flow inputs invalidates the frozen physical sign-off and requires a fresh GDS/precheck/gate-level sign-off before submitting a new revision.

Documentation-only changes do not alter the frozen silicon implementation, but the final portal revision should still be checked against the intended Git commit.
