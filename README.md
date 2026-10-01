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

## Roadmap

1. ✅ Streaming signed INT8 MAC baseline
2. ✅ Deterministic 4-element INT8 dot-product engine
3. ✅ Numerical-width reduction from 24-bit to provably sufficient 18-bit accumulation
4. ✅ 40 MHz setup/hold timing closure across reported corners
5. ✅ PPA A/B comparison of saturation implementations; retained the higher-margin comparator clamp
6. ✅ Tiny Tapeout precheck and gate-level regression on the 18-bit/40 MHz implementation
7. ⏳ Evaluate strict max-slew cleanup without trading away timing margin
8. ⏳ Shuttle submission hardening
