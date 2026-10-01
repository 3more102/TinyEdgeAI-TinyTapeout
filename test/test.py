# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge


def u8(value: int) -> int:
    return value & 0xFF


def sat8(value: int) -> int:
    return max(-128, min(127, value))


async def sample_after_active_edge(dut):
    """Wait through the active edge and sample after half a cycle.

    The falling-edge sample point is intentionally shared by RTL and gate-level
    simulations. It gives the post-layout unit-delay clock/data network time to
    settle before outputs are converted to integers.
    """
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)


async def tick(dut, activation: int, weight: int, enable: int = 1):
    dut.ena.value = enable
    dut.ui_in.value = u8(activation)
    dut.uio_in.value = u8(weight)
    await sample_after_active_edge(dut)


async def reset(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Two reset edges make initialization robust for both RTL and the
    # back-annotated gate-level clock network.
    await sample_after_active_edge(dut)
    await sample_after_active_edge(dut)

    dut.rst_n.value = 1


async def send_vector(dut, activations, weights):
    assert len(activations) == 4
    assert len(weights) == 4

    previous = int(dut.uo_out.value)
    for index, (activation, weight) in enumerate(zip(activations, weights)):
        await tick(dut, activation, weight)
        if index < 3:
            assert int(dut.uo_out.value) == previous

    expected = sat8(sum(a * w for a, w in zip(activations, weights)))
    assert int(dut.uo_out.value) == u8(expected)


@cocotb.test()
async def test_dot4_nominal_and_back_to_back(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    assert int(dut.uo_out.value) == 0
    assert int(dut.uio_oe.value) == 0

    await send_vector(dut, [3, 5, -2, 4], [4, 2, 3, -1])
    assert int(dut.uo_out.value) == 12

    await send_vector(dut, [1, 2, 3, 4], [5, 6, 7, 8])
    assert int(dut.uo_out.value) == 70


@cocotb.test()
async def test_saturation(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    await send_vector(dut, [127, 127, 127, 127], [127, 127, 127, 127])
    assert int(dut.uo_out.value) == 0x7F

    await send_vector(dut, [-128, -128, -128, -128], [127, 127, 127, 127])
    assert int(dut.uo_out.value) == 0x80


@cocotb.test()
async def test_enable_pauses_vector(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    await tick(dut, 2, 3)
    await tick(dut, 4, 5)

    # Disabled cycles must not advance the 4-sample transaction.
    await tick(dut, 100, 100, enable=0)
    await tick(dut, -100, -100, enable=0)
    assert int(dut.uo_out.value) == 0

    await tick(dut, 6, 7)
    assert int(dut.uo_out.value) == 0

    await tick(dut, 8, 9)
    assert int(dut.uo_out.value) == u8(sat8(2 * 3 + 4 * 5 + 6 * 7 + 8 * 9))


@cocotb.test()
async def test_randomized_reference_model(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    rng = random.Random(0x54494E59)

    for _ in range(64):
        activations = [rng.randint(-128, 127) for _ in range(4)]
        weights = [rng.randint(-128, 127) for _ in range(4)]
        await send_vector(dut, activations, weights)
