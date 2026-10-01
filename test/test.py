# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


def u8(value: int) -> int:
    return value & 0xFF


async def cycle(dut, activation: int, weight: int):
    dut.ui_in.value = u8(activation)
    dut.uio_in.value = u8(weight)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def reset(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.rst_n.value = 1


@cocotb.test()
async def test_mac_accumulation_and_saturation(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    assert int(dut.uo_out.value) == 0
    assert int(dut.uio_oe.value) == 0

    await cycle(dut, 3, 4)
    assert int(dut.uo_out.value) == 12

    await cycle(dut, 5, 2)
    assert int(dut.uo_out.value) == 22

    await reset(dut)
    await cycle(dut, -3, 5)
    assert int(dut.uo_out.value) == u8(-15)

    await reset(dut)
    await cycle(dut, 127, 127)
    assert int(dut.uo_out.value) == 0x7F

    await reset(dut)
    await cycle(dut, -128, 127)
    assert int(dut.uo_out.value) == 0x80


@cocotb.test()
async def test_enable_gates_accumulation(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    await reset(dut)

    dut.ena.value = 0
    await cycle(dut, 10, 10)
    assert int(dut.uo_out.value) == 0

    dut.ena.value = 1
    await cycle(dut, 10, 10)
    assert int(dut.uo_out.value) == 100
