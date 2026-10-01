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

## Saturation implementation

The selected RTL uses an explicit signed clamp after the complete 18-bit dot product:

- values above +127 produce `0x7F`;
- values below -128 produce `0x80`;
- values inside the INT8 range pass through unchanged.

A sign-extension-fit implementation was also proven functionally equivalent over the complete signed 18-bit domain, but physical A/B characterization showed that it reduced only three synthesized cells while losing about 1.17 ns of worst setup margin and increasing strict max-slew violations. The explicit comparator clamp was therefore retained.

## Physical-design target

The original 24-bit design at 50 MHz had approximately -0.692 ns worst setup slack. The selected 18-bit design is therefore targeted at **40 MHz / 25 ns**. The final characterized comparator-clamp configuration adds post-global-routing design repair with a 50% slew margin. At commit `8ee235a9`, it closes setup and hold across every reported corner with **+6.1106 ns** worst setup slack and **+0.1100 ns** worst hold slack, while reporting **zero** strict 0.75 ns max-slew violations.
