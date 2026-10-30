"""The LMT84 and amplifier chain (A3 or A0, and A1), and the potentiometer (A5)."""

import pytest

# Worked out by hand from the Rev C schematic, independent of analog_shield.py:
# U2A gain 4.3509 and offset 0.6481 V (rail at 5 V), then R14/R15 = 0.41107, so
# TEMP_SIG = 1.78855 * Vs - 0.26641.
GAIN = 4.3509
OFFSET = 0.6481
DIVIDER = 0.41107

# LMT84 datasheet table 3: degrees C -> mV
LMT84_TABLE = [(-40, 1247), (0, 1034), (25, 898), (50, 760), (100, 476), (150, 183)]


def temp_sig(sensor_v):
    return (GAIN * sensor_v - OFFSET) * DIVIDER


def ext_spi(fake):
    (spi,) = [s for s in fake.SPI.instances if s.id == 0]
    return spi


def set_a3_a5(pd, fake, volts):
    """Queues the MAX11635's next result (A3-A5): 2.048 V full scale."""
    pd.external_adc()
    code = min(4095, round(volts * 4096 / 2.048))
    ext_spi(fake).responses.append(bytes((code >> 8, code & 0xFF)))


def set_a0_a2(fake, gpio, volts):
    """Sets an RP2040 ADC input (A0 is GPIO26, A1 GPIO27): 3.3 V full scale."""
    fake.ADC.values[gpio] = min(4095, round(volts * 4096 / 3.3)) << 4


def test_gain_and_offset_match_the_schematic(shield):
    assert shield.amplifier_gain() == pytest.approx(GAIN, rel=1e-4)
    assert shield.amplifier_offset_volts() == pytest.approx(OFFSET, rel=1e-4)


@pytest.mark.parametrize("celsius,mv", LMT84_TABLE)
def test_temperature_from_volts_matches_datasheet_table(shield, celsius, mv):
    assert shield.temperature_from_volts(mv / 1000) == pytest.approx(celsius, abs=0.5)


@pytest.mark.parametrize("celsius,mv", LMT84_TABLE[1:4])
def test_temperature_on_a3(shield, pd, fake, celsius, mv):
    set_a3_a5(pd, fake, temp_sig(mv / 1000))
    assert shield.temperature() == pytest.approx(celsius, abs=0.5)


@pytest.mark.parametrize("celsius,mv", LMT84_TABLE[1:4])
def test_temperature_on_a0(shield, fake, celsius, mv):
    shield.set_output_pin("a0")
    set_a0_a2(fake, 26, temp_sig(mv / 1000))
    assert shield.temperature() == pytest.approx(celsius, abs=0.5)


def test_each_stage_of_the_chain(shield, pd, fake):
    set_a3_a5(pd, fake, 1.2)
    assert shield.output_volts() == pytest.approx(1.2, abs=0.001)
    set_a3_a5(pd, fake, 1.2)
    assert shield.amplifier_volts() == pytest.approx(1.2 / DIVIDER, abs=0.002)
    set_a3_a5(pd, fake, 1.2)
    assert shield.sensor_volts() == pytest.approx((1.2 / DIVIDER + OFFSET) / GAIN, abs=0.001)


def test_output_is_read_on_a3_by_default(shield, pd, fake):
    set_a3_a5(pd, fake, 1.0)
    shield.output_volts()
    assert ext_spi(fake).writes[-1] == [0x80 | 0 << 3 | 0x06]  # MAX11635 channel 0 is A3


def test_raw_sensor_volts_reads_a1(shield, fake):
    set_a0_a2(fake, 27, 0.9)
    assert shield.raw_sensor_volts() == pytest.approx(0.9, abs=0.001)


def test_supply_moves_the_offset(shield):
    shield.set_supply_volts(5.2)
    assert shield.amplifier_offset_volts() == pytest.approx(OFFSET * 5.2 / 5, rel=1e-4)
    assert shield.amplifier_gain() == pytest.approx(GAIN, rel=1e-4)  # gain doesn't depend on it


@pytest.mark.parametrize("volts", [3.3, 6.5, 0])
def test_supply_out_of_range(shield, volts):
    with pytest.raises(ValueError, match="4-6 V"):
        shield.set_supply_volts(volts)


@pytest.mark.parametrize("name", ["A1", "A5", "D3", 3, None])
def test_output_pin_must_be_a3_or_a0(shield, name):
    with pytest.raises(ValueError, match="'A3' or 'A0'"):
        shield.set_output_pin(name)


def test_pot_reads_a5(shield, pd, fake):
    set_a3_a5(pd, fake, 1.5)
    assert shield.pot_volts() == pytest.approx(1.5, abs=0.001)
    assert ext_spi(fake).writes[-1] == [0x80 | 2 << 3 | 0x06]  # MAX11635 channel 2 is A5
