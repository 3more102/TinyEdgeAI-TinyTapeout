# TinyEdgeAI-TinyTapeout

TinyEdgeAI is a compact streaming signed-INT8 multiply-accumulate (MAC) accelerator designed for Tiny Tapeout and the SKY130-based TTSKY26d flow.

## Current architecture

- Signed INT8 activation input: `ui_in[7:0]`
- Signed INT8 weight input: `uio_in[7:0]`
- One MAC operation per enabled clock cycle
- 24-bit internal accumulator
- Saturating signed INT8 output on `uo_out[7:0]`
- Active-low reset through `rst_n`
- `ena` gates accumulation
- Bidirectional pins are configured as inputs

The first milestone is intentionally small and verifiable: a reusable edge-AI MAC primitive that can later grow into a dot-product engine, quantized neuron, or compact inference accelerator while remaining realistic for Tiny Tapeout area constraints.

## Repository layout

- `src/` — synthesizable Verilog RTL and LibreLane configuration
- `test/` — cocotb testbench and simulation Makefile
- `docs/` — Tiny Tapeout project documentation
- `info.yaml` — Tiny Tapeout project metadata and pinout
- `.github/workflows/` — RTL test, GDS, documentation, and optional FPGA workflows

## Verification

The cocotb suite checks reset, positive and negative MAC behavior, enable gating, accumulation, and signed INT8 saturation.

Run locally:

```bash
cd test
python -m pip install -r requirements.txt
make -B
```

## Tiny Tapeout target

This repository follows the official `TinyTapeout/ttsky-verilog-template` structure and SKY26d GitHub Actions flow.

## Roadmap

1. Baseline streaming INT8 MAC
2. Deterministic vector/dot-product controller
3. Quantization and activation options
4. Area/timing optimization after GDS feedback
5. Gate-level regression and submission hardening
