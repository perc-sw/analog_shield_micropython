"""The two LEDs, which light when their pin is low."""

import pytest

# From the Rev C PCB netlist (analog_shield.kicad_pcb): LED1 (green D1) on D6, LED2 (red D2) on D5.
GREEN_GPIO = 10  # D6
RED_GPIO = 9  # D5


def test_version_returns_dunder_version(shield):
    assert shield.version() == shield.__version__


@pytest.mark.parametrize("name,gpio", [("green_led", GREEN_GPIO), ("red_led", RED_GPIO)])
def test_led_starts_off_and_is_active_low(shield, fake, name, gpio):
    led = getattr(shield, name)
    assert led.value() == 0
    assert fake.Pin.levels[gpio] == 1  # high: off
    led.on()
    assert fake.Pin.levels[gpio] == 0
    assert led.value() == 1
    led.off()
    assert fake.Pin.levels[gpio] == 1


def test_toggle_and_set_value(shield, fake):
    shield.red_led.toggle()
    assert fake.Pin.levels[RED_GPIO] == 0
    shield.red_led.toggle()
    assert fake.Pin.levels[RED_GPIO] == 1
    shield.red_led.value(1)
    assert fake.Pin.levels[RED_GPIO] == 0
    shield.red_led.value(0)
    assert fake.Pin.levels[RED_GPIO] == 1


def test_leds_are_independent(shield, fake):
    shield.green_led.on()
    assert fake.Pin.levels[GREEN_GPIO] == 0
    assert fake.Pin.levels.get(RED_GPIO) is None  # red not set up until used


def test_pin_is_set_up_once(shield, fake):
    shield.green_led.on()
    shield.green_led.off()
    shield.green_led.toggle()
    assert [c for c in fake.Pin.created if c[0] == GREEN_GPIO] == [
        (GREEN_GPIO, fake.Pin.OUT, None, {"value": 1})]
