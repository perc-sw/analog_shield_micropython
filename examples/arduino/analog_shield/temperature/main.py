# Prints the temperature from the shield's LMT84 sensor once a second.
#
# Needs analog_shield.py on the board, JP4 on 5 V, JP1 on INT (the on-board
# sensor) and JP2 on EXT (the amplifier to A3). With JP2 on INT, change the
# set_output_pin() line to "A0". Hold the sensor (U1) to see it warm up.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

import analog_shield as shield  # the Analog Shield library, used as shield.<name>


def setup():
    shield.set_output_pin("A3")  # JP2 on EXT


def loop():
    print("%.1f C" % shield.temperature())  # 1 decimal place
    delay(1000)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
