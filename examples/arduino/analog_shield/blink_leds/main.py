# Blinks the shield's green and red LEDs in turn, each for half a second.
#
# Needs JP3 (VIO) on 3.3 V. Each LED lights when its pin is LOW: the pin
# pulls current through the LED from VIO.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...

GREEN_LED = 6  # D6 (D1 on the shield)
RED_LED = 5  # D5 (D2 on the shield)


def setup():
    pinMode(GREEN_LED, OUTPUT)
    pinMode(RED_LED, OUTPUT)


def loop():
    digitalWrite(GREEN_LED, LOW)  # green on
    digitalWrite(RED_LED, HIGH)  # red off
    delay(500)  # wait half a second
    digitalWrite(GREEN_LED, HIGH)
    digitalWrite(RED_LED, LOW)
    delay(500)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
