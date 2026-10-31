# Prints the temperature on A3 once a second, with the green LED lit while it runs.
#
# Needs analog_shield.py on the board, JP3 (VIO) on 3.3 V, JP4 on 5 V, JP1 on
# INT (the on-board sensor) and JP2 on EXT (the amplifier to A3). With JP2 on
# INT, change the set_output_pin() line to "A0". The green LED goes off again
# when the script is stopped with Interrupt (Ctrl-C).

import time  # sleep() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>
import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

shield.set_output_pin("A3")  # JP2 on EXT
mcu.analog_averaging(16)  # average 16 samples per reading: steadier
shield.green_led.on()  # green on (D6 low): the script is running

try:
    while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
        print("%.1f C" % shield.temperature())  # 1 decimal place
        time.sleep(1)
finally:  # runs when the loop is stopped, even by Interrupt
    shield.green_led.off()  # green off (D6 high): the script has stopped
