# TinyEdgeAI — 4-Element INT8 Dot-Product Accelerator

## How it works

TinyEdgeAI computes a fixed-length four-element signed INT8 dot product using one multiplier reused across four clock cycles.

For each enabled rising edge:

1. `ui_in[7:0]` is interpreted as a signed INT8 activation.
2. `uio_in[7:0]` is interpreted as a signed INT8 weight.
3. The pair is multiplied as signed 8x8 arithmetic.
4. The signed 16-bit product is sign-extended into a 24-bit accumulator.

Every four accepted samples, the complete dot product is saturated to [-128, 127] and copied to `uo_out[7:0]`. The internal accumulator and 2-bit sample counter then restart automatically for the next vector. The published result is held stable during accumulation of the next vector.

Driving `rst_n` low clears the partial vector and the output result. When `ena` is low, no sample is accepted and the vector position is preserved.

## How to test

Apply four activation/weight pairs on consecutive enabled rising edges.

Example:

| Cycle | Activation | Weight | Product |
| --- | ---: | ---: | ---: |
| 1 | 3 | 4 | 12 |
| 2 | 5 | 2 | 10 |
| 3 | -2 | 3 | -6 |
| 4 | 4 | -1 | -4 |

The completed dot product is 12 and appears on `uo_out` after cycle 4.

A new independent four-sample vector starts on the next accepted clock edge. Values above +127 saturate to 0x7F; values below -128 saturate to 0x80.

## External hardware

No external hardware is required for the baseline project.
