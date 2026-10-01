# TinyEdgeAI verification

The project uses cocotb with Icarus Verilog for RTL simulation.

## Run

```sh
python -m pip install -r requirements.txt
make -B
```

The regression covers reset, signed multiplication, accumulation, enable gating, positive saturation, and negative saturation. The Tiny Tapeout GitHub workflow also runs the same suite automatically on every push.
