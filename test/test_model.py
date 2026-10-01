# SPDX-License-Identifier: Apache-2.0

INT18_MIN = -(1 << 17)
INT18_MAX = (1 << 17) - 1
INT18_MASK = (1 << 18) - 1


def clamp_int8(value: int) -> int:
    return max(-128, min(127, value))


def rtl_saturate_int8_model(value: int) -> int:
    """Bit-accurate model of the RTL sign-extension saturation test."""
    assert INT18_MIN <= value <= INT18_MAX

    raw = value & INT18_MASK
    bit7 = (raw >> 7) & 1
    upper = (raw >> 8) & 0x3FF
    expected_upper = 0x3FF if bit7 else 0x000

    if upper == expected_upper:
        return raw & 0xFF
    if (raw >> 17) & 1:
        return 0x80
    return 0x7F


def test_saturation_equivalence_exhaustive_over_signed_18_bit_domain():
    for value in range(INT18_MIN, INT18_MAX + 1):
        assert rtl_saturate_int8_model(value) == (clamp_int8(value) & 0xFF)


def test_signed_int8_product_and_dot4_bounds_exhaustive():
    products = [a * w for a in range(-128, 128) for w in range(-128, 128)]
    assert min(products) == -16256
    assert max(products) == 16384

    # Four terms can independently attain either product extreme.
    assert 4 * min(products) == -65024
    assert 4 * max(products) == 65536

    # Signed 18-bit range contains the complete four-product range.
    assert INT18_MIN <= -65024
    assert 65536 <= INT18_MAX
