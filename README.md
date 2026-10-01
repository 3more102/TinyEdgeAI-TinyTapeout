# TinyEdgeAI-TinyTapeout

TinyEdgeAI is a compact fixed-length signed-INT8 dot-product accelerator designed for Tiny Tapeout and the SKY130-based TTSKY26d flow.

## Architecture

The datapath consumes one signed INT8 activation/weight pair per enabled clock cycle. Four consecutive pairs form one vector transaction:

`dot4 = a0*w0 + a1*w1 + a2*w2 + a3*w3`

After the fourth accepted sample, the **18-bit** accumulated sum is saturated to signed INT8 and atomically published on `uo_out[7:0]`. The output remains stable while the next four-sample vector is being accumulated.

### Interface

- `ui_in[7:0]` — signed INT8 activation
- `uio_in[7:0]` — signed INT8 weight
- `uo_out[7:0]` — most recently completed saturated dot-product
- `clk` — transaction clock; current physical-design target is 40 MHz
- `rst_n` — active-low reset and vector-boundary restart
- `ena` — when low, accumulation and the sample counter pause
- `uio_oe = 0` — bidirectional pins remain inputs

This time-multiplexed architecture preserves full INT8 operands while fitting Tiny Tapeout's compact I/O interface.

## Verification

The cocotb regression checks:

- deterministic four-sample transaction boundaries
- signed positive/negative arithmetic
- back-to-back vectors
- exact INT8 saturation thresholds at 127, 128, -128, and -129
- exact accumulator extrema at +65536 and -65024
- enable/pause behavior
- reset during a partial vector
- fixed bidirectional-output configuration
- 512 deterministic randomized vectors against a Python reference model
- RTL and gate-level sampling using the same half-cycle observation point

Run locally:

```bash
cd test
python -m pip install -r requirements.txt
make -B
```

## Tiny Tapeout flow

The repository follows the current official `TinyTapeout/ttsky-verilog-template` structure and uses the `ttsky26d` GitHub Actions flow for RTL tests, GDS generation, precheck, gate-level regression, documentation, and optional FPGA generation.

## TTSKY26d submission status

Verified on **2026-10-01**:

- TTSKY26d is open for submission and has an official closing date of **2026-11-30**.
- The repository matches the current SKY Verilog template metadata format (`yaml_version: 6`).
- Post-merge `main` CI run #32 passes the RTL/model, documentation, and GDS flows.
- Silicon readiness and external portal submission are tracked separately.
- The project is **not claimed as submitted** until a specific revision is confirmed in the Tiny Tapeout portal.

See [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md) for the release freeze, CI evidence, and remaining portal steps.

## Silicon-readiness snapshot

Characterized source/config commit: `8ee235a90029046bc8b1b79f9874e5f64df463ae`

- target: **40 MHz / 25 ns**, **1x1** Tiny Tapeout tile, SKY130 / `ttsky26d`
- RTL regression: **6/6 passed**, including **512 deterministic randomized vectors**
- exhaustive arithmetic checks: all **262,144 signed 18-bit values** for saturation equivalence and all **65,536 INT8 operand pairs** for product bounds
- synthesized cells: **612**
- synthesized cell area: **6478.7136 µm²**
- post-route standard-cell utilization: **44.7201%**
- worst setup slack: **+6.1106 ns**
- worst hold slack: **+0.1100 ns**
- strict 0.75 ns max-slew violations: **0**
- max-capacitance / max-fanout violations: **0 / 0**
- routing DRC / Magic DRC / LVS: **clear / clear / clear**
- Tiny Tapeout precheck: **passed**
- gate-level cocotb regression: **6/6 passed**
- GDS artifact: **generated**
- final PR silicon gates: **PASS** on run #29; PR #1 is **merged**
- post-merge `main` validation: **PASS** on run #32

## Roadmap

1. ✅ Streaming signed INT8 MAC baseline
2. ✅ Deterministic 4-element INT8 dot-product engine
3. ✅ Numerical-width reduction from 24-bit to provably sufficient 18-bit accumulation
4. ✅ 40 MHz setup/hold timing closure across reported corners
5. ✅ PPA A/B comparison of saturation implementations; retained the higher-margin comparator clamp
6. ✅ Tiny Tapeout precheck and gate-level regression on the 18-bit/40 MHz implementation
7. ✅ Post-route slew repair with zero strict 0.75 ns max-slew violations
8. ✅ Final silicon sign-off completed and PR #1 merged
9. ⏳ Submit and confirm the exact TTSKY26d revision in the Tiny Tapeout portal
