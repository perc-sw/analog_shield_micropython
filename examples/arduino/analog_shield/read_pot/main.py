# Prints the potentiometer's (RV1) reading ten times a second, 0-1023.
#
# RV1 goes from 0 V to VIO (JP3) and is read on A5, where 1023 is 2.048 V:
# with VIO at 3.3 V, the last third or so of the turn reads 1023.

from arduino import *  # the Arduino-style functions: pinMode(), digitalWrite(), delay(), ...


def setup():
    pass  # nothing to set up: A5 is always an analogue input


def loop():
    print(analogRead(A5))  # 0-1023
    delay(100)


# Do not edit below this line: it runs setup() once, then loop() over and over.
def main():
    setup()  # runs once, at the start
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        loop()


# True when this file is run, but not when another file imports it.
if __name__ == "__main__":
    main()
