# Changelog

## 0.1.0-rc.1 (unreleased)

First version.

- `analog_shield.py`: one-file library for the Analog Shield (Rev C) on a Phyduino Pico, on top of the `phyduino.py` built into the Phyduino Pico firmware.
  - `green_led` and `red_led` (D6, D5), which light when their pin is low: `on()`, `off()`, `toggle()`, `value()`.
  - `encoder()`: the rotary encoder on D3/D4, counted by pin interrupts, with `position()` (one per click), `steps()`, `set_position()`, and the push switch on D2 with `pressed()` and `on_press()` (debounced, run with `micropython.schedule()`).
  - `temperature()`: the LMT84 through the TLV2472 amplifier, with each stage of the chain in volts: `raw_sensor_volts()` (A1), `sensor_volts()`, `amplifier_volts()`, `output_volts()` (A3 or A0, chosen with `set_output_pin()` to match JP2), plus `temperature_from_volts()`, `amplifier_gain()`, `amplifier_offset_volts()` and `set_supply_volts()` for the +5V rail.
  - `pot_volts()`: the potentiometer on A5.
  - `version()`: the library version, as in `__version__`.
- `package.json`, so `mpremote mip install github:perc-sw/analog_shield_micropython` installs it. Each GitHub release also has `analog_shield.py` and a compiled `analog_shield.mpy` attached, with their SHA-256.
- 6 examples in two sets, `examples/arduino/analog_shield/` (`setup()` and `loop()`, with `arduino.py`) and `examples/phyduino/analog_shield/` (plain MicroPython, with `phyduino.py`): `blink_leds`, `encoder_counter`, `encoder_led_brightness`, `read_pot`, `temperature` and `amplifier_chain`.
- Host tests (pytest) with a fake `machine` module, against `phyduino.py` from phyduino_pico_micropython v0.1.0-rc.1.
- Documentation site (`docs/`) with a Doxygen API reference generated from the docstrings, published to GitHub Pages.

### Known issues

- A5 reads at most 2.048 V, so with JP3 (VIO) on 3.3 V the last third or so of the potentiometer's turn reads full scale.
- After `mcu.pwm("D6")` or `analogWrite(6, ...)`, `green_led` no longer changes the LED: the pin stays on PWM (the same for `red_led` and D5). Call `mcu.pin("D6", "out")` to free it.
- The J2 sensor connector (A4) has no functions; read it with `mcu.analog_volts("A4")`.
