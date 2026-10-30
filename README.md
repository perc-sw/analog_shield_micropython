# Analog Shield MicroPython Library

[![CI](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/ci.yml/badge.svg)](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/ci.yml)
[![Docs](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/docs.yml/badge.svg)](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/docs.yml)
[![Release](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/release.yml/badge.svg)](https://github.com/perc-sw/analog_shield_micropython/actions/workflows/release.yml)
[![Version](https://img.shields.io/github/v/release/perc-sw/analog_shield_micropython?include_prereleases&label=version)](https://github.com/perc-sw/analog_shield_micropython/releases)
[![Licence](https://img.shields.io/github/license/perc-sw/analog_shield_micropython?label=licence)](LICENSE)
[![MicroPython](https://img.shields.io/badge/MicroPython-v1.29.0-2B2728?logo=micropython&logoColor=white)](https://micropython.org/)

A one-file MicroPython library for the [Analog Shield](https://github.com/perc-sw/analog_shield)
on a [Phyduino Pico](https://github.com/perc-sw/phyduino_pico_micropython), used in the University
of Toronto, Department of Physics,
"[Introduction to Electronics](https://plrs.physics.utoronto.ca/course-listing/)" course.

### Documentation: <https://perc-sw.github.io/analog_shield_micropython/>

It works on top of the `phyduino.py` library built into the Phyduino Pico firmware, and gives
names to the shield's parts:

- The green and red LEDs, which light when their pin is low.
- The rotary encoder and its push switch, counted by pin interrupts.
- The LMT84 temperature sensor, read through the shield's two-stage op-amp amplifier, with the
  voltage at each stage of the amplifier.
- The potentiometer.

### Example script

```python
import analog_shield as shield

shield.green_led.on()
print(shield.temperature())          # degrees C, from the on-board LMT84
print(shield.encoder().position())   # clicks turned, + clockwise
print(shield.pot_volts())            # 0-2.048 V
```

## Set up

### 1. Set up the Phyduino Pico (once)

Put the Phyduino Pico firmware on the board, as in the
[Phyduino Pico set-up](https://github.com/perc-sw/phyduino_pico_micropython#set-up). It has
`phyduino.py` and `arduino.py` built in, which this library needs.

### 2. Set the shield's jumpers

Set these before plugging the shield in. The Phyduino Pico's pins are 3.3 V only.

| Jumper | Set to | Does |
|---|---|---|
| JP3 (VIO, solder) | **3.3 V** | Encoder pull-ups, LEDs and the potentiometer on 3.3 V, safe for the Phyduino's pins |
| JP4 (solder) | **5 V** | The amplifier and sensor on the Arduino 5 V supply. Not VIN above 6 V |
| JP1 | INT | The on-board LMT84 feeds the amplifier (EXT: the sensor on J1) |
| JP2 | EXT | The amplifier's output to A3, the Phyduino's more accurate ADC (INT: to A0) |

JP3 and JP4 come open: bridge one side of each. With neither side of JP4 bridged the amplifier
has no supply; with neither side of JP3 the encoder and LEDs don't work.

### 3. Put the library on the board

Either:

- download `analog_shield.py` (or the smaller, compiled `analog_shield.mpy`) from this
  repository's [Releases](https://github.com/perc-sw/analog_shield_micropython/releases) page and
  copy it to the board: `mpremote cp analog_shield.py :`. In PyCharm, upload it with the
  **MicroPython Tools** plugin next to your `main.py`;
- or install it from GitHub: `mpremote mip install github:perc-sw/analog_shield_micropython`
  (into `/lib` on the board).

To check it is there:

```
mpremote exec "import analog_shield; print(analog_shield.version())"
```

Then run your own `main.py` as on the Phyduino Pico (`mpremote run main.py`, or from PyCharm).

## Pins

| Shield part | Pin | Notes |
|---|---|---|
| Green LED (D1) | D6 | On when low: `green_led` |
| Red LED (D2) | D5 | On when low: `red_led` |
| Encoder A, B (ENC1) | D3, D4 | Pull-ups and RC filters on the shield: `encoder()` |
| Encoder push switch | D2 | Low while pressed: `encoder().pressed()` |
| Amplifier output (TEMP_SIG) | A3 (JP2 on EXT) or A0 (JP2 on INT) | 0-2.05 V: `output_volts()` |
| Sensor voltage (SENSOR_IN) | A1 | Before the amplifier: `raw_sensor_volts()` |
| Potentiometer (RV1) | A5 | 0 V to VIO: `pot_volts()` |
| Sensor connector J2 | A4 | No functions here; `mcu.analog_volts("A4")` |

The other header pins are free. D5 and D6 share PWM slices with D19 and A0
(see [phyduino's `pwm()`](https://perc-sw.github.io/phyduino_pico_micropython/)).

## Reference

| Function | Does |
|---|---|
| `green_led`, `red_led`: `.on()`, `.off()`, `.toggle()`, `.value()` | The shield's LEDs |
| `encoder()` | The rotary encoder, set up on the first call |
| `encoder().position()`, `.steps()`, `.set_position(clicks=0)` | Clicks turned (+ clockwise), raw steps (4 per click), set the count |
| `encoder().pressed()`, `.on_press(callback)` | The push switch now; a function to call on each press |
| `temperature()` | LMT84 temperature in °C, through the amplifier |
| `sensor_volts()`, `raw_sensor_volts()` | The sensor's voltage, worked out from the amplifier or read directly on A1 |
| `amplifier_volts()`, `output_volts()` | The amplifier's output (J8 pin 4), and after the divider on A3/A0 |
| `amplifier_gain()`, `amplifier_offset_volts()` | U2A: output = sensor × gain − offset |
| `temperature_from_volts(volts)` | The LMT84's datasheet curve, volts to °C |
| `set_output_pin("A3" or "A0")` | Match JP2 (A3 at start-up) |
| `set_supply_volts(volts)` | The measured +5V rail, for a more accurate offset (5.0 at start-up) |
| `pot_volts()` | The potentiometer on A5, 0-2.048 V |
| `version()` | The library version |

For steadier analogue readings, call `mcu.analog_averaging(16)` from `phyduino.py`.

### The amplifier

```
LMT84 ─JP1─ SENSOR_IN (A1) ─► U2A: × 4.35 − 0.648 V ─► U2B: 10.7 kHz low-pass ─► OPA_OUT (J8-4)
                                                                                     │ R14/R15 × 0.411
                                                                                     ▼
                                                                         TEMP_SIG ─JP2─ A3 or A0
```

The offset comes from the R1/R2 divider on the +5V rail, so it changes with the rail: measure it
and call `set_supply_volts()` for the best accuracy. The chain spreads about −50 to 150 °C over
A3's 0-2.048 V.

## Examples

There are two sets of the same examples, as for the Phyduino Pico:

- `examples/arduino/analog_shield/` uses the Arduino-style functions (`from arduino import *`),
  laid out with `setup()` and `loop()`; leave the `main()` at the end of each file as it is.
- `examples/phyduino/analog_shield/` uses `phyduino.py` (`import phyduino as mcu`), written the
  usual MicroPython way, with a `while True:` loop.

Each example is a `main.py` in its own folder, with a header comment saying how to set the jumpers
and what it prints. With `analog_shield.py` on the board, run one with
`mpremote run examples/phyduino/analog_shield/temperature/main.py`, or copy its `main.py` to the
board so it runs at start-up.

| Example (in `arduino/` and `phyduino/`) | Shows |
|---|---|
| `analog_shield/blink_leds/` | Blinking the green and red LEDs in turn |
| `analog_shield/encoder_counter/` | Counting the encoder's clicks; a press sets it back to 0 |
| `analog_shield/encoder_led_brightness/` | Setting the green LED's brightness with the encoder |
| `analog_shield/read_pot/` | The potentiometer's reading on A5 |
| `analog_shield/temperature/` | The LMT84's temperature through the amplifier |
| `analog_shield/amplifier_chain/` | The voltage at each stage of the amplifier |

## Development

The tests run on a PC against a fake `machine` module, with `phyduino.py` and `arduino.py` from a
[phyduino_pico_micropython](https://github.com/perc-sw/phyduino_pico_micropython) checkout next to
this one (or the folder in `PHYDUINO_PATH`):

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt     # .venv/bin/python on macOS/Linux
.venv\Scripts\python -m pytest tests
doxygen                                                          # API reference into docs/wiki/
```

## Licence

GPL-3.0. See [LICENSE](LICENSE).
