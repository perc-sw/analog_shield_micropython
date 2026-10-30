# Prints the potentiometer's (RV1) voltage ten times a second.
#
# Needs analog_shield.py on the board. RV1 goes from 0 V to VIO (JP3) and is
# read on A5, which measures up to 2.048 V: with VIO at 3.3 V, the last third
# or so of the turn reads 2.048 V.

import time  # sleep() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    print("%.3f V" % shield.pot_volts())  # 3 decimal places: 1 mV
    time.sleep(0.1)
