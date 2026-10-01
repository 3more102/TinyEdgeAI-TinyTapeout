# TinyEdgeAI Silicon Sign-Off

This document is the release-freeze checklist for PR #1 and the Tiny Tapeout submission candidate.

## Candidate identity

- Repository: `3more102/TinyEdgeAI-TinyTapeout`
- Pull request: #1
- Branch: `feature/int8-dot4-engine`
- Tiny Tapeout top module: `tt_um_3more102_tinyedgeai`
- Target: SKY130 / `ttsky26d`
- Tile: `1x1`
- Clock: 40 MHz
- Clock period: 25 ns
- Characterized source/config commit: `8ee235a90029046bc8b1b79f9874e5f64df463ae`
- Release-hardening predecessor commit: `8aa1947e883baf0c4f95963a8158c92227affa3a`
- Final PR head: `f5f9bddeb6662d3eb89059fabe67a3e48a625b6b`
- Verified PR synthetic-merge tree: `913eaaaa68e7c52f0c90a3398c76a4928a73a45c`
- Actual merged `main` commit: `b46c1581f383f8154c74109b662be0c51d7162d1`

GitHub PR workflows checked out the synthetic merge ref for the final PR head. A direct commit comparison between `913eaaaa...` and the actual merge commit `b46c1581...` reports zero changed files, so the silicon-tested tree is the same tree that was merged to `main`.

The commits after the characterized source/config commit contain documentation and CI-trigger hardening only. Any later change to RTL, `src/config.json`, `info.yaml`, pin mapping, or physical-flow inputs invalidates the physical evidence below and requires a fresh sign-off run.

## RTL

- [x] Deterministic synchronous active-low reset behavior implemented
- [x] Signed INT8 operands declared explicitly
- [x] 8x8 signed product width is 16 bits
- [x] Product is explicitly sign-extended to 18 bits
- [x] Accumulator is explicitly signed and 18 bits wide
- [x] Four-product mathematical range proven as [-65024, +65536]
- [x] 18-bit signed range proven sufficient
- [x] Saturation thresholds are explicit at +127 and -128
- [x] Completed output is registered and held stable during the next transaction
- [x] Unused Tiny Tapeout bidirectional outputs are driven deterministically
- [x] No architecture change is required for release freeze

## Functional verification

The selected regression contains six cocotb tests plus exhaustive Python arithmetic checks.

- [x] Zero vector
- [x] Nominal positive arithmetic
- [x] Signed positive/negative arithmetic
- [x] Back-to-back vectors
- [x] Exact saturation checks at +127, +128, -128, -129
- [x] Exact accumulator extrema at +65536 and -65024
- [x] Enable/pause checks at every transaction phase
- [x] Reset checks during partial transactions
- [x] Output stability while a new vector accumulates
- [x] 512 deterministic randomized vectors against an independent Python model
- [x] Exhaustive saturation-model equivalence over all 262,144 signed 18-bit values
- [x] Exhaustive signed INT8 product-bound enumeration over all 65,536 operand pairs

## Physical evidence

Source/config characterization began at `8ee235a90029046bc8b1b79f9874e5f64df463ae`. Final PR GDS run #29 reproduced the same silicon results on the verified PR merge tree `913eaaaa68e7c52f0c90a3398c76a4928a73a45c`, whose tree matches merged commit `b46c1581f383f8154c74109b662be0c51d7162d1`:

- [x] Synthesis completed
- [x] Synthesized cells: 612
- [x] Synthesized cell area: 6478.7136 µm²
- [x] Post-route standard-cell count: 913
- [x] Post-route standard-cell area: 7375.82 µm²
- [x] Post-route standard-cell utilization: 44.7201%
- [x] Worst setup slack: +6.1106 ns at `max_ss_100C_1v60`
- [x] Worst hold slack: +0.1100 ns at `min_ff_n40C_1v95`
- [x] Setup violations: 0
- [x] Hold violations: 0
- [x] Strict 0.75 ns max-slew violations: 0 across reported corners
- [x] Max-capacitance violations: 0
- [x] Max-fanout violations: 0
- [x] Routing DRC: 0
- [x] Magic DRC: 0
- [x] LVS errors: 0
- [x] GDS generated
- [x] No unconstrained functional timing paths: post-route `check_setup -unconstrained_endpoints -no_clock -no_input_delay` produced no findings in all nine reported corners

The selected post-global-routing repair keeps the transition constraint unchanged and uses `GRT_DESIGN_REPAIR_MAX_SLEW_PCT=50`; it is a repair setting, not a checker relaxation.

## Tiny Tapeout integration

- [x] Top module matches `info.yaml`
- [x] `ui_in[7:0]` maps to signed activation
- [x] `uio_in[7:0]` maps to signed weight
- [x] `uo_out[7:0]` maps to the completed saturated result
- [x] `uio_out = 8'h00`
- [x] `uio_oe = 8'h00`
- [x] `clock_hz = 40000000`
- [x] `tiles = 1x1`
- [x] Source-file list contains `project.v` and `tinyedgeai_core.v`
- [x] Tiny Tapeout precheck passed on the characterized candidate
- [x] Gate-level cocotb regression passed 6/6 on the characterized candidate

## CI release gate

PR workflows are intentionally configured to run on `pull_request`, on pushes to `main`, and by manual dispatch. This avoids relying on stale branch-push evidence when deciding whether PR #1 is ready.

The final PR candidate is verified:

- [x] RTL/model workflow PASS — run #29
- [x] GDS build PASS — run #29
- [x] Tiny Tapeout precheck PASS — run #29
- [x] Gate-level regression PASS — 6/6 on run #29
- [x] Silicon-relevant reports and artifacts belong to the final PR workflow run and verified merge tree

Artifact metadata associates run #29 with final PR head `f5f9bddeb6662d3eb89059fabe67a3e48a625b6b`; the workflow checkout/physical artifact records synthetic merge commit `913eaaaa68e7c52f0c90a3398c76a4928a73a45c`. That tree has zero file differences from actual merged commit `b46c1581f383f8154c74109b662be0c51d7162d1`.

The optional layout viewer may fail if GitHub Pages is not enabled; it is not a silicon gate.

## Reproduction

### RTL and arithmetic regression

```bash
python -m pip install -r test/requirements.txt
python -m pytest -q test/test_model.py
cd test
make clean
make
python -m cocotb_tools.check_results results.xml
```

Expected CI environment:

- Ubuntu 24.04 runner
- Python 3.11
- pytest 8.4.2
- cocotb 2.1.0
- Icarus Verilog installed from the Ubuntu runner package repository

### Tiny Tapeout physical flow

The canonical physical sign-off path is the repository workflow:

```bash
gh workflow run gds.yaml --ref main
```

The workflow uses:

- `TinyTapeout/tt-gds-action@ttsky26d`
- PDK `sky130A`
- Tiny Tapeout precheck from the same `ttsky26d` action line
- Tiny Tapeout gate-level test action from the same `ttsky26d` action line

## Post-merge main validation

The frozen implementation was revalidated after merge on `main` commit `d7aa270db0ec7e4ed8e8fdffed6ea5af006c7bbb`. The commits after the merge are documentation-only relative to `b46c1581f383f8154c74109b662be0c51d7162d1`.

- [x] RTL/model workflow PASS — run #32
- [x] Docs workflow PASS — run #32
- [x] GDS workflow PASS — run #32

External Tiny Tapeout submission remains a separate step. See `docs/SUBMISSION_CHECKLIST.md`; the project is not considered submitted until a specific revision is confirmed in the Tiny Tapeout portal.

## Release hygiene

- [x] Apache-2.0 license present
- [x] Generated simulation results ignored
- [x] Gate-level generated netlist ignored
- [x] Local merged configuration files ignored
- [x] No local absolute machine path is required by the checked release files
- [x] Architecture and physical-design evidence are documented
- [x] Rejected comparator-free saturation experiment is documented and not selected
- [x] Strict slew constraint was not hidden or relaxed
- [x] Final PR CI evidence checked; PR #1 subsequently left Draft and was merged

## Final release state

- PR #1: **MERGED**
- final PR head: `f5f9bddeb6662d3eb89059fabe67a3e48a625b6b`
- verified PR merge tree: `913eaaaa68e7c52f0c90a3398c76a4928a73a45c`
- actual merge commit: `b46c1581f383f8154c74109b662be0c51d7162d1`
- release-gate status: **SATISFIED**
- GitHub release/tag: not yet created

Non-blocking observations:

- optional layout-viewer deployment fails with HTTP 404 because GitHub Pages is not enabled; GDS generation itself is successful
- final parasitic annotation reports 16 unannotated `HI` constant-driver entries and 0 partially unannotated drivers; no timing violation results from them

Any future change to RTL, `src/config.json`, `info.yaml`, pin mapping, or physical-flow inputs invalidates this sign-off and requires a fresh silicon gate.
