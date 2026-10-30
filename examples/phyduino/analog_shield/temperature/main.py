# Prints the temperature from the shield's LMT84 sensor once a second.
#
# Needs analog_shield.py on the board, JP4 on 5 V, JP1 on INT (the on-board
# sensor) and JP2 on EXT (the amplifier to A3). With JP2 on INT, change the
# set_output_pin() line to "A0". Hold the sensor (U1) to see it warm up.

import time  # sleep() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>
import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

shield.set_output_pin("A3")  # JP2 on EXT
mcu.analog_averaging(16)  # average 16 samples per reading: steadier

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    print("%.1f C" % shield.temperature())  # 1 decimal place
    time.sleep(1)
