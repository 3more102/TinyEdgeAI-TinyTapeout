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

Evidence recorded for commit `8ee235a90029046bc8b1b79f9874e5f64df463ae`:

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
- [ ] Exact final unconstrained-functional-path count must be confirmed from the current-head timing report before release freeze

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

The final PR HEAD must show:

- [ ] RTL/model workflow PASS
- [ ] GDS build PASS
- [ ] Tiny Tapeout precheck PASS
- [ ] Gate-level regression PASS
- [ ] Silicon-relevant reports correspond to the same final HEAD

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
gh workflow run gds.yaml --ref feature/int8-dot4-engine
```

The workflow uses:

- `TinyTapeout/tt-gds-action@ttsky26d`
- PDK `sky130A`
- Tiny Tapeout precheck from the same `ttsky26d` action line
- Tiny Tapeout gate-level test action from the same `ttsky26d` action line

## Release hygiene

- [x] Apache-2.0 license present
- [x] Generated simulation results ignored
- [x] Gate-level generated netlist ignored
- [x] Local merged configuration files ignored
- [x] No local absolute machine path is required by the checked release files
- [x] Architecture and physical-design evidence are documented
- [x] Rejected comparator-free saturation experiment is documented and not selected
- [x] Strict slew constraint was not hidden or relaxed
- [ ] Final-head CI evidence must be checked before changing PR #1 from Draft to Ready for Review

## Freeze rule

Do not mark PR #1 Ready for Review, merge it, or create a submission tag until every unchecked item above has objective evidence from the final PR HEAD. If the HEAD changes after a passing run, repeat the gate.
