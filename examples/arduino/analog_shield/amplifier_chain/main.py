# Prints the voltage at each stage of the temperature amplifier, once a
# second, as columns:
#   A1       the sensor's voltage, read directly
#   sensor   the sensor's voltage, worked out back from the amplifier's output
#   opamp    the amplifier's output (J8 pin 4), sensor * gain - offset
#   A3       the amplifier's output after the R14/R15 divider
#
# Needs analog_shield.py on the board, JP4 on 5 V, JP1 on INT and JP2 on EXT.
# Check the opamp column with a meter on J8 pin 4. With JP1 on EXT, the
# sensor on J1 is measured instead.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

import analog_shield as shield  # the Analog Shield library, used as shield.<name>


def setup():
    print("gain %.3f, offset %.3f V" % (shield.amplifier_gain(), shield.amplifier_offset_volts()))
    print("A1      sensor  opamp   A3")


def loop():
    print("%.3f   %.3f   %.3f   %.3f" % (
        shield.raw_sensor_volts(),
        shield.sensor_volts(),
        shield.amplifier_volts(),
        shield.output_volts(),
    ))
    delay(1000)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
