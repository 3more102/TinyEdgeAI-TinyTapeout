# Physical Design Evidence

## Final candidate architecture

TinyEdgeAI uses one signed 8x8 multiplier, an 18-bit accumulator, and a 40 MHz / 25 ns physical target. The accumulator width is lossless for a four-element INT8 dot product: individual products span [-16256, +16384], so the complete four-term sum spans [-65024, +65536]. Signed 17-bit storage is insufficient by one positive count; signed 18-bit storage safely covers the full range.

## Baseline dot4 — 24-bit accumulator at 50 MHz

Characterized RTL commit: `90277073bbc5b6cc93808656130a62dd0636e815`

- synthesized cells: **762**
- synthesized cell area: **8032.704 µm²**
- sequential area: **723.1936 µm²**
- worst setup slack: **-0.6923 ns**
- worst hold slack: **+0.1076 ns**
- routing DRC: clear
- Magic DRC: clear
- LVS: clear

The design fit physically, but 50 MHz was not timing-clean at the reported slow corners.

## 18-bit comparator-clamp candidate — 40 MHz

Characterized RTL/config commit: `f1f0b390b23f0906fa79b70a1774354f327c5604`

- synthesized cells: **612**
- synthesized cell area: **6478.7136 µm²**
- sequential area: **595.5712 µm²**
- nominal TT setup slack: **+12.0391 ns**
- worst setup slack: **+4.2926 ns**
- worst hold slack: **+0.1100 ns**
- setup violations: **0**
- hold violations: **0**
- max-capacitance violations: **0**
- max-fanout violations: **0**
- strict 0.75 ns max-slew violations: **219**
- routing DRC: clear
- Magic DRC: clear
- LVS: clear
- Tiny Tapeout precheck: passed
- gate-level cocotb regression: passed

Versus the 24-bit/50 MHz implementation, this reduced synthesized cell count by **150 cells (19.7%)** and synthesized cell area by **1553.9904 µm² (19.3%)**, while moving worst setup slack from negative to strongly positive.

## Saturation micro-optimization A/B experiment

A later experiment replaced explicit signed magnitude clamps with a sign-extension-fit test. The function was exhaustively checked over all **262,144 signed 18-bit values** and was logically equivalent to clamping to [-128, +127].

Characterized source/config represented by commit `9cc185969a40e92ef2d2ee64b867acc02c0c1c94`:

- synthesized cells: **609**
- synthesized cell area: **6476.2112 µm²**
- worst setup slack: **+3.1205 ns**
- worst hold slack: **+0.1109 ns**
- setup violations: **0**
- hold violations: **0**
- strict 0.75 ns max-slew violations: **248**
- routing DRC: clear
- Magic DRC: clear
- LVS: clear

The experiment saved only **3 synthesized cells** and **2.5024 µm²** versus the comparator-clamp candidate, but reduced worst setup margin by about **1.1721 ns** and increased strict max-slew violations by **29**. It was therefore rejected. The final candidate restores the explicit signed clamp.

## Remaining transition-quality observation

The chosen comparator-clamp implementation reports **219 max-slew violations** only under the deliberately strict 0.75 ns transition constraint at slow corners. Setup/hold, max capacitance, max fanout, DRC, LVS, Tiny Tapeout precheck, and gate-level regression are clean.

This item remains explicitly tracked rather than hidden by simply relaxing the constraint. Any transition-repair experiment must be re-characterized for area, timing, DRC/LVS, and gate-level behavior before adoption.

## CI note

The Tiny Tapeout layout viewer deploys through GitHub Pages. Pages is not currently enabled for this repository, so viewer deployment can return a 404 even when the GDS is valid. The viewer is treated as optional; GDS, precheck, and gate-level regression remain the silicon-relevant gates.
