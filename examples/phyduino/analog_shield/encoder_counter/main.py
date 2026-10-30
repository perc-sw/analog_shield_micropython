# Prints the rotary encoder's position each time it changes: one count per
# click, up clockwise and down anticlockwise. Pressing the knob sets it back
# to 0.
#
# Needs analog_shield.py on the board and JP3 (VIO) on 3.3 V. The encoder is
# read by pin interrupts, so no click is missed while the loop sleeps.

import time  # sleep_ms() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>

knob = shield.encoder()  # sets up D2-D4 and starts counting from 0


def reset():  # runs each time the knob is pressed
    knob.set_position(0)


knob.on_press(reset)

last = None  # the position last printed; None so the first one prints

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    position = knob.position()
    if position != last:  # only print when it has changed
        print(position)
        last = position
    time.sleep_ms(10)  # a short pause; the counting carries on meanwhile
