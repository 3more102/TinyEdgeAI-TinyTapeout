# Architecture

## Datapath

TinyEdgeAI uses a time-multiplexed signed INT8 multiplier feeding a 24-bit accumulator. Reusing one multiplier avoids the area cost of four parallel multipliers.

```text
ui_in[7:0]  ---- activation ----\
                              signed 8x8 multiply --> sign extend --> accumulator
uio_in[7:0] ---- weight -------/                            |
                                                           | every 4 samples
                                                           v
                                                    INT8 saturation
                                                           |
                                                           v
                                                     uo_out[7:0]
```

## Transaction model

A two-bit counter tracks accepted samples. Only `ena=1` advances the state. On sample four, the final product is included in the sum, the saturated result is committed, and the accumulator/counter return to zero.

This creates deterministic, back-to-back four-element vector transactions without sacrificing any operand bits for control signaling.

## Numerical behavior

Each signed INT8 product is in [-16256, 16384]. Four products therefore fit safely in the 24-bit accumulator. Saturation is applied only after the full dot product is complete, avoiding intermediate clipping.
