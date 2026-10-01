# Architecture

## Datapath

TinyEdgeAI uses a time-multiplexed signed INT8 multiplier feeding an **18-bit accumulator**. Reusing one multiplier avoids the area cost of four parallel multipliers.

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

## Numerical proof for accumulator width

For signed INT8 operands:

- the largest positive product is `(-128) * (-128) = +16384`
- the most negative product is `(-128) * 127 = -16256`
- four products are therefore bounded by `[-65024, +65536]`

A signed 17-bit value can represent at most +65535, so 17 bits are insufficient by exactly one count. Signed **18-bit** storage spans `[-131072, +131071]`, which safely contains the complete dot-product range.

This proof allows the accumulator and associated adder to be reduced from 24 bits to 18 bits without numerical loss.

## Physical-design target

The first 50 MHz dot4 characterization (commit `9027707`) completed GDS but reported worst setup slack of approximately -0.692 ns at the max slow corner. The design target is therefore set to 40 MHz / 25 ns pending final post-route characterization.
