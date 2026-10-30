"""@package analog_shield
@brief Analog Shield library for the Phyduino Pico, in MicroPython.

Copy this file to the board next to your own main.py, then:
@code
import analog_shield as shield

shield.green_led.on()
print(shield.temperature())  # degrees C, from the on-board LMT84
print(shield.encoder().position())
@endcode

Needs the Phyduino Pico firmware, which has phyduino.py built in. Set the
shield's jumpers for a 3.3 V board: JP3 (VIO) on 3.3 V, JP4 on 5 V, JP1 on INT
and JP2 on EXT (the amplifier to A3).

| Shield part | Pin |
|---|---|
| Green LED (D1), red LED (D2) | D6, D5 (both on when low) |
| Encoder A, B, push switch | D3, D4, D2 (low when closed) |
| Amplifier output | A3 (JP2 on EXT) or A0 (JP2 on INT) |
| Sensor voltage before the amplifier | A1 |
| Potentiometer RV1 | A5 |

Licence: GPL-3.0.
"""

import math
import time

import micropython
from machine import Pin
from micropython import const

import phyduino as mcu

## Library version, MAJOR.MINOR.PATCH.
__version__ = "0.1.0-rc.1"


def version():
    """@brief Gets the library version.

    @return The version string, MAJOR.MINOR.PATCH, e.g. "0.1.0-rc.1".

    @par Example
    @code
    print(shield.version())
    @endcode
    @ingroup shield_api
    """
    return __version__

# --- LEDs -------------------------------------------------------------------------

class Led:
    """@brief One of the shield's LEDs, D1 (green) or D2 (red).

    Each LED runs from VIO through 1 kOhm to its pin, so the pin turns it on by
    pulling low. on() and off() hide that: on() drives the pin low. The pin is
    set up the first time the LED is used, starting with the LED off.

    @note After phyduino's pwm() on the same pin, on() and off() no longer
    change the LED. Call mcu.pin(name, "out") to free the pin.

    @code
    shield.green_led.on()
    shield.red_led.toggle()
    @endcode
    @ingroup leds
    """

    def __init__(self, name):
        """@brief Gives a LED on a header pin; the shield's are green_led and red_led.

        @param name Pin the LED's cathode is on, e.g. "D6".
        """
        self._name = name
        self._pin = None

    def _get(self):
        if self._pin is None:
            self._pin = mcu.pin(self._name, "out", value=1)  # high: off
        return self._pin

    def on(self):
        """@brief Turns the LED on."""
        self._get().value(0)

    def off(self):
        """@brief Turns the LED off."""
        self._get().value(1)

    def toggle(self):
        """@brief Turns the LED on if it is off, and off if it is on."""
        p = self._get()
        p.value(not p.value())

    def value(self, level=None):
        """@brief Reads or sets the LED.

        @param level None to read; 1 (on) or 0 (off) to set.
        @return 1 (on) or 0 (off) when reading; None when setting.
        """
        if level is None:
            return 0 if self._get().value() else 1
        self._get().value(0 if level else 1)


## @brief The green LED, D1 on the shield, on pin D6: a Led object.
# @ingroup leds
green_led = Led("D6")

## @brief The red LED, D2 on the shield, on pin D5: a Led object.
# @ingroup leds
red_led = Led("D5")

# --- Rotary encoder (D2-D4) -------------------------------------------------------

# Encoder state is (A << 1) | B. The step for each change of state, indexed by
# (old << 2) | new: +1 one way, -1 the other, 0 for no change or a skipped
# state (both lines changed at once, e.g. contact bounce).
_TRANSITIONS = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)
_STEPS_PER_DETENT = const(4)  # PEC11L: one full A/B cycle per click
_PRESS_DEBOUNCE_MS = const(50)  # the RC filter only covers about 50 us


class Encoder:
    """@brief The shield's rotary encoder (ENC1) and its push switch.

    A and B (D3, D4) and the switch (D2) have pull-ups and RC filters on the
    shield, so the pins are inputs with no pull of their own. Pin interrupts
    count each change of A and B, so no turn is missed while your program does
    something else. Use encoder() to get the shield's instance rather than
    making another.

    Turning clockwise counts up, one per click.

    @ingroup encoder
    """

    def __init__(self):
        """@brief Sets up D2-D4 as inputs and starts counting from 0."""
        self._a = mcu.pin("D3", "in")
        self._b = mcu.pin("D4", "in")
        self._switch = mcu.pin("D2", "in")
        self._state = (self._a.value() << 1) | self._b.value()
        self._steps = 0
        self._callback = None
        self._last_press = None
        self._run_callback_ref = self._run_callback  # made once: the interrupt can't allocate
        # Hard interrupts, so each edge is read straight away: a late read can
        # miss a state and lose a step
        both = Pin.IRQ_RISING | Pin.IRQ_FALLING
        self._a.irq(handler=self._step, trigger=both, hard=True)
        self._b.irq(handler=self._step, trigger=both, hard=True)

    def _step(self, _pin):
        # Hard interrupt handler: integers only, as it can't allocate memory
        state = (self._a.value() << 1) | self._b.value()
        self._steps += _TRANSITIONS[(self._state << 2) | state]
        self._state = state

    def _press(self, _pin):
        now = time.ticks_ms()
        if self._last_press is not None and \
                time.ticks_diff(now, self._last_press) < _PRESS_DEBOUNCE_MS:
            return  # switch bounce after a press already counted
        self._last_press = now
        try:
            micropython.schedule(self._run_callback_ref, 0)
        except RuntimeError:
            pass  # schedule queue full: this press is dropped

    def _run_callback(self, _arg):
        callback = self._callback
        if callback is not None:
            callback()

    def position(self):
        """@brief Gets the number of clicks turned since the start or set_position().

        @return Clicks, positive clockwise and negative anticlockwise.
        """
        return self._steps // _STEPS_PER_DETENT

    def steps(self):
        """@brief Gets the raw count: four steps per click.

        @return Steps since the start or set_position().
        """
        return self._steps

    def set_position(self, clicks=0):
        """@brief Sets the count, e.g. back to 0.

        @param clicks The new position() value.
        """
        self._steps = clicks * _STEPS_PER_DETENT

    def pressed(self):
        """@brief Reads the push switch now.

        @return True while the knob is pressed in.
        """
        return self._switch.value() == 0

    def on_press(self, callback):
        """@brief Calls a function each time the knob is pressed.

        The function runs soon after the press, between lines of your
        program (MicroPython's micropython.schedule()), and takes no arguments.
        Presses within 50 ms of the last one are taken as switch bounce.

        @param callback A function, or None to stop.

        @par Example
        @code
        def pressed():
            shield.encoder().set_position(0)

        shield.encoder().on_press(pressed)
        @endcode
        """
        self._callback = callback
        if callback is None:
            self._switch.irq(handler=None)
        else:
            self._switch.irq(handler=self._press, trigger=Pin.IRQ_FALLING)


_encoder = None


def encoder():
    """@brief Gets the shield's rotary encoder.

    The first call sets up D2-D4 and starts counting from 0.

    @return The Encoder object (the same one every call).

    @par Example
    @code
    knob = shield.encoder()
    print(knob.position(), knob.pressed())
    @endcode
    @ingroup encoder
    """
    global _encoder
    if _encoder is None:
        _encoder = Encoder()
    return _encoder

# --- Temperature sensor and amplifier (A0/A3, A1) ---------------------------------

# U2A, a non-inverting amplifier with an offset: the sensor voltage Vs on its
# + input (through R13), and R3 from the R1/R2 divider to its - input with R4
# as feedback. Vout = Vs * (1 + R4 / Rin) - Vref * R4 / Rin, where Vref and Rin
# include the divider's own resistance (R1 parallel to R2).
_R1 = 16_900  # +5V to Vref
_R2 = 680  # Vref to GND
_R3 = 10_000  # Vref to the - input
_R4 = 35_700  # feedback
# U2B is a unity-gain filter (about 10.7 kHz). R14 and R15 divide its output
# down to the ADC's range.
_R14 = 10_000  # amplifier output to TEMP_SIG
_R15 = 6_980  # TEMP_SIG to GND
_DIVIDER = _R15 / (_R14 + _R15)  # 0.41107

# LMT84 transfer function (TI datasheet, equation 1):
# mV = 870.6 - 5.506 * (T - 30) - 0.00176 * (T - 30) ** 2
_LMT84_MV_AT_30C = 870.6
_LMT84_SLOPE = 5.506
_LMT84_CURVE = 0.00176

_OUTPUT_PINS = ("A3", "A0")  # JP2 on EXT, JP2 on INT
_output_pin = "A3"
_supply_volts = 5.0


def set_output_pin(name):
    """@brief Selects the pin the amplifier's output is read on, to match jumper JP2.

    JP2 on EXT connects the amplifier to A3, read by the Phyduino's MAX11635
    against its 2.048 V reference (0.5 mV steps). JP2 on INT connects it to
    A0, read by the RP2040 (0.8 mV steps, less accurate).

    @param name "A3" (the default) or "A0".
    @exception ValueError Not "A3" or "A0".
    @ingroup temperature
    """
    global _output_pin
    key = name.strip().upper() if isinstance(name, str) else name
    if key not in _OUTPUT_PINS:
        raise ValueError(
            "JP2 connects the amplifier to A3 (EXT) or A0 (INT); use 'A3' or 'A0'")
    _output_pin = key


def set_supply_volts(volts=5.0):
    """@brief Sets the voltage of the shield's +5V rail, for a more accurate offset.

    The amplifier's offset comes from a divider on the +5V rail (selected by
    JP4), so it moves with the supply: 0.1 V off gives about 0.5 °C. Measure
    the rail (J8 pin 1 to pin 3) and give the value here.

    @param volts The rail voltage, 4-6 V.
    @exception ValueError Not 4-6 V.
    @ingroup temperature
    """
    global _supply_volts
    if not 4.0 <= volts <= 6.0:
        raise ValueError("the +5V rail should be 4-6 V; measure it between J8 pins 1 and 3")
    _supply_volts = volts


def _input_resistance():
    return _R3 + _R1 * _R2 / (_R1 + _R2)


def amplifier_gain():
    """@brief The amplifier's (U2A) gain, from the shield's resistor values.

    @return 1 + R4 / (R3 + R1 || R2), about 4.35.
    @ingroup temperature
    """
    return 1 + _R4 / _input_resistance()


def amplifier_offset_volts():
    """@brief The voltage the amplifier (U2A) takes off its output.

    Its output is sensor_volts() * amplifier_gain() - amplifier_offset_volts().

    @return Volts, about 0.648 V with the rail at 5 V (see set_supply_volts()).
    @ingroup temperature
    """
    vref = _supply_volts * _R2 / (_R1 + _R2)
    return vref * _R4 / _input_resistance()


def output_volts():
    """@brief Reads the signal at the end of the chain (TEMP_SIG) on A3 or A0.

    This is the amplifier's output after the R14/R15 divider, about 0-2.05 V.
    Set the pin with set_output_pin(). Use mcu.analog_averaging() for steadier
    readings.

    @return Volts (a float).
    @exception OSError The Phyduino's external ADC did not respond (A3).
    @ingroup temperature
    """
    return mcu.analog_volts(_output_pin)


def amplifier_volts():
    """@brief Works out the amplifier's output (OPA_OUT), before the R14/R15 divider.

    Also on J8 pin 4, to check with a meter.

    @return Volts, 0-5 V (a float).
    @exception OSError The Phyduino's external ADC did not respond (A3).
    @ingroup temperature
    """
    return output_volts() / _DIVIDER


def sensor_volts():
    """@brief Works out the sensor's voltage (SENSOR_IN) from the amplifier's output.

    The sensor is the on-board LMT84 with JP1 on INT, or the one on J1 with JP1
    on EXT. The amplifier covers about 0.15-1.29 V.

    @return Volts (a float).
    @exception OSError The Phyduino's external ADC did not respond (A3).
    @ingroup temperature
    """
    return (amplifier_volts() + amplifier_offset_volts()) / amplifier_gain()


def raw_sensor_volts():
    """@brief Reads the sensor's voltage (SENSOR_IN) directly, on A1.

    No amplifier, so about three times coarser than sensor_volts(). The two
    should agree to within about 10 mV.

    @return Volts (a float).
    @ingroup temperature
    """
    return mcu.analog_volts("A1")


def temperature_from_volts(volts):
    """@brief Converts an LMT84 output voltage to a temperature.

    Uses the datasheet's parabolic fit, accurate to about 0.5 °C over -50 to
    150 °C.

    @param volts The sensor's output in volts, about 0.18-1.30 V.
    @return Degrees C (a float).
    @ingroup temperature
    """
    mv = volts * 1000
    root = math.sqrt(_LMT84_SLOPE ** 2 + 4 * _LMT84_CURVE * (_LMT84_MV_AT_30C - mv))
    return (_LMT84_SLOPE - root) / (2 * -_LMT84_CURVE) + 30


def temperature():
    """@brief Reads the on-board LMT84 temperature sensor through the amplifier.

    Needs JP1 on INT and JP2 set as in set_output_pin(). Covers about -50 to
    150 °C; outside that the amplifier's output is at a rail and the reading
    stops changing.

    @return Degrees C (a float).
    @exception OSError The Phyduino's external ADC did not respond (A3).

    @par Example
    @code
    print("%.1f C" % shield.temperature())
    @endcode
    @ingroup temperature
    """
    return temperature_from_volts(sensor_volts())

# --- Potentiometer (A5) -----------------------------------------------------------

def pot_volts():
    """@brief Reads the potentiometer, RV1, on A5.

    The wiper goes from 0 V to VIO (set by JP3). A5 is on the Phyduino's
    MAX11635, which reads at most 2.048 V: with VIO at 3.3 V the last third
    or so of the turn reads 2.048 V.

    @return Volts, 0-2.048 V (a float).
    @exception OSError The Phyduino's external ADC did not respond.

    @par Example
    @code
    print(shield.pot_volts())
    @endcode
    @ingroup pot
    """
    return mcu.analog_volts("A5")
