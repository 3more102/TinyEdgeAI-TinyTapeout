# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge


CLOCK_PERIOD_NS = 25
RANDOM_VECTOR_COUNT = 512
RANDOM_SEED = 0x54494E59


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
    assert int(dut.uio_oe.value) == 0
    assert int(dut.uio_out.value) == 0


async def reset(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Two reset edges make initialization robust for both RTL and the
    # gate-level clock network.
    await sample_after_active_edge(dut)
    await sample_after_active_edge(dut)

    assert int(dut.uo_out.value) == 0
    assert int(dut.uio_oe.value) == 0
    assert int(dut.uio_out.value) == 0
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


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, CLOCK_PERIOD_NS, unit="ns").start())


@cocotb.test()
async def test_zero_nominal_signed_and_back_to_back(dut):
    await start_clock(dut)
    await reset(dut)

    await send_vector(dut, [0, 0, 0, 0], [0, 0, 0, 0])
    assert int(dut.uo_out.value) == 0

    await send_vector(dut, [3, 5, -2, 4], [4, 2, 3, -1])
    assert int(dut.uo_out.value) == 12

    await send_vector(dut, [-3, -2, 1, 4], [4, 5, 2, -1])
    assert int(dut.uo_out.value) == u8(-24)

    await send_vector(dut, [-8, 7, -6, 5], [-4, -3, 2, 1])
    assert int(dut.uo_out.value) == 4

    # Immediate next vector proves transaction restart/back-to-back behavior.
    await send_vector(dut, [1, 2, 3, 4], [5, 6, 7, 8])
    assert int(dut.uo_out.value) == 70


@cocotb.test()
async def test_saturation_boundaries(dut):
    await start_clock(dut)
    await reset(dut)

    vectors = [
        ([127, 0, 0, 0], [1, 0, 0, 0], 127),
        ([64, 0, 0, 0], [2, 0, 0, 0], 127),    # +128 -> +127
        ([-128, 0, 0, 0], [1, 0, 0, 0], -128),
        ([-43, 0, 0, 0], [3, 0, 0, 0], -128),  # -129 -> -128
    ]

    for activations, weights, expected in vectors:
        await send_vector(dut, activations, weights)
        assert int(dut.uo_out.value) == u8(expected)


@cocotb.test()
async def test_enable_pauses_every_transaction_phase(dut):
    await start_clock(dut)

    activations = [1, 2, 3, 4]
    weights = [2, 2, 2, 2]
    expected = u8(sum(a * w for a, w in zip(activations, weights)))

    for phase in range(4):
        await reset(dut)

        for index in range(phase):
            await tick(dut, activations[index], weights[index])
            assert int(dut.uo_out.value) == 0

        held = int(dut.uo_out.value)
        for activation, weight in [(127, 127), (-128, -128), (55, -99)]:
            await tick(dut, activation, weight, enable=0)
            assert int(dut.uo_out.value) == held

        for index in range(phase, 4):
            await tick(dut, activations[index], weights[index])
            if index < 3:
                assert int(dut.uo_out.value) == held

        assert int(dut.uo_out.value) == expected


@cocotb.test()
async def test_reset_discards_partial_vector_after_each_phase(dut):
    await start_clock(dut)

    partial_a = [10, -20, 30]
    partial_w = [7, 6, -5]

    for accepted_samples in (1, 2, 3):
        await reset(dut)

        for index in range(accepted_samples):
            await tick(dut, partial_a[index], partial_w[index])
            assert int(dut.uo_out.value) == 0

        await reset(dut)
        assert int(dut.uo_out.value) == 0

        await send_vector(dut, [1, 1, 1, 1], [1, 2, 3, 4])
        assert int(dut.uo_out.value) == 10


@cocotb.test()
async def test_accumulator_extrema_and_extreme_patterns(dut):
    await start_clock(dut)
    await reset(dut)

    # Exact maximum sum: 4 * (-128 * -128) = +65536.
    await send_vector(dut, [-128, -128, -128, -128], [-128, -128, -128, -128])
    assert int(dut.uo_out.value) == 0x7F

    # Exact minimum sum: 4 * (-128 * 127) = -65024.
    await send_vector(dut, [-128, -128, -128, -128], [127, 127, 127, 127])
    assert int(dut.uo_out.value) == 0x80

    # Alternating extreme signs exercise cancellation and signed extension.
    activations = [-128, 127, -128, 127]
    weights = [-128, 127, 127, -128]
    await send_vector(dut, activations, weights)
    expected = sat8(sum(a * w for a, w in zip(activations, weights)))
    assert int(dut.uo_out.value) == u8(expected)


@cocotb.test()
async def test_randomized_reference_model(dut):
    await start_clock(dut)
    await reset(dut)

    rng = random.Random(RANDOM_SEED)

    for _ in range(RANDOM_VECTOR_COUNT):
        activations = [rng.randint(-128, 127) for _ in range(4)]
        weights = [rng.randint(-128, 127) for _ in range(4)]
        await send_vector(dut, activations, weights)
