# Prints the rotary encoder's position each time it changes: one count per
# click, up clockwise and down anticlockwise. Pressing the knob sets it back
# to 0.
#
# Needs analog_shield.py on the board and JP3 (VIO) on 3.3 V. The encoder is
# read by pin interrupts, so no click is missed during delay().

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

import analog_shield as shield  # the Analog Shield library, used as shield.<name>

knob = None  # the encoder, set up in setup()
last = None  # the position last printed; None so the first one prints


def reset():  # runs each time the knob is pressed
    knob.set_position(0)


def setup():
    global knob
    knob = shield.encoder()  # sets up D2-D4 and starts counting from 0
    knob.on_press(reset)


def loop():
    global last
    position = knob.position()
    if position != last:  # only print when it has changed
        print(position)
        last = position
    delay(10)  # a short pause; the counting carries on meanwhile


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
