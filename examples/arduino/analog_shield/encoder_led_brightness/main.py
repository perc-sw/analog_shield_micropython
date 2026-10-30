# Sets the green LED's brightness with the rotary encoder: 20 clicks from off
# to full. Prints the brightness in percent when it changes.
#
# Needs analog_shield.py on the board and JP3 (VIO) on 3.3 V. The LED lights
# when D6 is LOW, so analogWrite() sets the time it is *off*: full brightness
# is 0.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

import analog_shield as shield  # the Analog Shield library, used as shield.<name>

GREEN_LED = 6  # D6 (D1 on the shield)
STEPS = 20  # clicks from off to full brightness

knob = None  # the encoder, set up in setup()
last = None  # the brightness last printed


def setup():
    global knob
    knob = shield.encoder()  # sets up D2-D4 and starts counting from 0
    analogWrite(GREEN_LED, 255)  # off


def loop():
    global last
    clicks = constrain(knob.position(), 0, STEPS)  # keep it between 0 and STEPS
    knob.set_position(clicks)  # so turning back past the end responds straight away
    analogWrite(GREEN_LED, 255 - map(clicks, 0, STEPS, 0, 255))  # the off time
    percent = map(clicks, 0, STEPS, 0, 100)
    if percent != last:
        print(percent, "%")
        last = percent
    delay(10)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
