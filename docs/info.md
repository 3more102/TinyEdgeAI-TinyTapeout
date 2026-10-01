# TinyEdgeAI — Streaming INT8 MAC Accelerator

## How it works

TinyEdgeAI implements a signed 8-bit multiply-accumulate datapath intended as the first silicon milestone of a compact quantized edge-AI accelerator.

On every rising clock edge while the design is enabled:

1. `ui_in[7:0]` is interpreted as a signed INT8 activation.
2. `uio_in[7:0]` is interpreted as a signed INT8 weight.
3. The two values are multiplied as a signed 8x8 operation.
4. The signed 16-bit product is sign-extended and accumulated into a 24-bit internal accumulator.
5. The accumulator is saturated to the signed INT8 range [-128, 127] and presented on `uo_out[7:0]`.

Driving `rst_n` low clears the accumulator. The bidirectional Tiny Tapeout pins are configured as inputs so that they carry the weight operand.

## How to test

Apply an activation on `ui_in` and a weight on `uio_in`. With `ena=1` and `rst_n=1`, each rising edge of `clk` performs one MAC update.

Examples:

- activation = 3, weight = 4 -> accumulated result = 12
- next activation = 5, weight = 2 -> accumulated result = 22
- values above +127 saturate to 0x7F
- values below -128 saturate to 0x80

To restart a dot product, assert `rst_n=0` for at least one rising clock edge.

## External hardware

No external hardware is required for the baseline design.
