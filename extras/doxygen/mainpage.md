# API reference

A one-file MicroPython library for the University of Toronto Department of
Physics Analog Shield on a Phyduino Pico. Set-up steps are on the
[home page](../index.html).

Copy `analog_shield.py` to the board next to your own `main.py`. It needs the
Phyduino Pico firmware, which has `phyduino.py` built in:

```{.py}
import analog_shield as shield

shield.green_led.on()
print(shield.temperature())  # degrees C, from the on-board LMT84
print(shield.encoder().position())
```

Everything on the Phyduino Pico (`mcu.pin()`, `mcu.pwm()`, `mcu.analog_volts()`,
...) still works alongside; see the
[Phyduino Pico MicroPython reference](https://perc-sw.github.io/phyduino_pico_micropython/).

## Jumpers {#jumpers}

Set these before plugging the shield in, for the Phyduino Pico's 3.3 V pins:

| Jumper | Set to | Does |
|---|---|---|
| JP3 (VIO) | 3.3 V | Pull-ups, LEDs and the potentiometer on 3.3 V, safe for the Phyduino's pins |
| JP4 | 5 V | The amplifier and sensor on the Arduino 5 V supply |
| JP1 | INT | The on-board LMT84 feeds the amplifier (EXT: the sensor on J1) |
| JP2 | EXT | The amplifier's output to A3 (INT: to A0; see set_output_pin()) |

JP3 and JP4 are solder jumpers and come open: bridge one side of each.

## Functions

`import analog_shield as shield`

| Topic | Use |
|---|---|
| @ref leds | `green_led`, `red_led`: Led.on(), Led.off(), Led.toggle(), Led.value() |
| @ref encoder | encoder(): Encoder.position(), Encoder.set_position(), Encoder.steps(), Encoder.pressed(), Encoder.on_press() |
| @ref temperature | temperature(), sensor_volts(), raw_sensor_volts(), amplifier_volts(), output_volts(), temperature_from_volts(), amplifier_gain(), amplifier_offset_volts(), set_output_pin(), set_supply_volts() |
| @ref pot | pot_volts() |
| @ref shield_api "Version" | version() |

Errors raise `ValueError` (a wrong setting) or `OSError` (the Phyduino's
external ADC did not respond), with a message saying what to do.

## Examples

The @ref example_scripts page lets you choose between the two sets of example
scripts in `examples/`, which have the same examples:
@ref examples_arduino (`examples/arduino/`, setup() and loop()) and
@ref examples_phyduino (`examples/phyduino/`, plain MicroPython).
