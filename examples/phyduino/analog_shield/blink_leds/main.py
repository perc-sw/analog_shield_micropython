# Blinks the shield's green and red LEDs in turn, each for half a second.
#
# Needs analog_shield.py on the board and JP3 (VIO) on 3.3 V. The LEDs light
# when their pin is low; green_led and red_led take care of that.

import time  # sleep() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    shield.green_led.on()  # green on (D6 low)
    shield.red_led.off()  # red off (D5 high)
    time.sleep(0.5)  # wait half a second
    shield.green_led.off()
    shield.red_led.on()
    time.sleep(0.5)
