# Physical Design Evidence

## Pre-optimization dot4 characterization

Characterized RTL commit: `90277073bbc5b6cc93808656130a62dd0636e815`

Tiny Tapeout flow: `ttsky26d` / SKY130A

Configuration at characterization:

- clock period: 20 ns (50 MHz)
- tile declaration: 1x1
- accumulator width: 24 bits

Observed synthesis/post-route evidence from the GitHub Actions GDS artifact:

- synthesized standard-cell count: **762**
- synthesized standard-cell area: **8032.704 µm²**
- sequential-cell area: **723.1936 µm²**
- nominal TT setup slack: **+7.8015 ns**
- worst reported setup slack: **-0.6923 ns** at the max slow corner
- hold worst slack: **+0.1076 ns**
- routing DRC checker: clear
- Magic DRC checker: clear
- LVS checker: clear

The GDS build itself completed successfully. The 50 MHz target was not considered timing-clean because the slow corners contained setup violations.

## Optimization response

Two changes follow directly from that evidence:

1. Reduce the accumulator from 24 bits to the mathematically sufficient 18 bits.
2. Change the physical target from 50 MHz to 40 MHz (25 ns).

A new post-route characterization is required before declaring final timing closure.
