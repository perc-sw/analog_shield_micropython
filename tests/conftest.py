"""Loads analog_shield.py on the PC with fake `machine`, `micropython` and `time` functions.

phyduino.py and arduino.py come from a phyduino_pico_micropython checkout: the
folder in PHYDUINO_PATH, or ../phyduino_pico_micropython next to this repository.
"""

import importlib
import os
import sys
import time
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHYDUINO_PATH = os.environ.get(
    "PHYDUINO_PATH", os.path.join(os.path.dirname(ROOT), "phyduino_pico_micropython"))
if not os.path.isfile(os.path.join(PHYDUINO_PATH, "phyduino.py")):
    raise RuntimeError(
        "phyduino.py not found in " + PHYDUINO_PATH + "; clone phyduino_pico_micropython "
        "next to this repository, or set PHYDUINO_PATH to its folder")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PHYDUINO_PATH)
sys.path.insert(0, ROOT)

import fake_machine  # noqa: E402

sys.modules["machine"] = fake_machine
# schedule() runs the function straight away: there is no main loop to wait for
sys.modules["micropython"] = types.SimpleNamespace(
    const=lambda value: value, schedule=lambda function, arg: function(arg))


class FakeClock:
    """MicroPython's ticks functions; each read moves time on by `step_us`."""

    def __init__(self):
        self.now_us = 0
        self.step_us = 1

    def ticks_us(self):
        self.now_us += self.step_us
        return self.now_us

    def ticks_ms(self):
        return self.ticks_us() // 1000

    def sleep_ms(self, ms):
        self.now_us += ms * 1000

    def sleep_us(self, us):
        self.now_us += us


clock = FakeClock()
time.ticks_us = clock.ticks_us
time.ticks_ms = clock.ticks_ms
time.ticks_diff = lambda new, old: new - old
time.sleep_ms = clock.sleep_ms
time.sleep_us = clock.sleep_us


@pytest.fixture
def pd():
    """A freshly loaded phyduino module with clean fake hardware."""
    fake_machine.reset()
    clock.now_us = 0
    clock.step_us = 1
    import phyduino

    return importlib.reload(phyduino)


@pytest.fixture
def shield(pd):
    """A freshly loaded analog_shield module, on top of a fresh phyduino."""
    import analog_shield

    return importlib.reload(analog_shield)


@pytest.fixture
def ard(pd):
    """A freshly loaded arduino module, on top of a fresh phyduino."""
    import arduino

    return importlib.reload(arduino)


@pytest.fixture
def fake():
    return fake_machine


@pytest.fixture
def fake_clock():
    return clock
