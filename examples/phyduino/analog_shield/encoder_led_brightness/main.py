# Sets the green LED's brightness with the rotary encoder: 20 clicks from off
# to full. Prints the brightness in percent when it changes.
#
# Needs analog_shield.py on the board and JP3 (VIO) on 3.3 V. The LED lights
# when D6 is low, so the PWM duty is the time it is *off*: full brightness is
# duty 0.

import time  # sleep_ms() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>
import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

STEPS = 20  # clicks from off to full brightness

knob = shield.encoder()  # sets up D2-D4 and starts counting from 0
led = mcu.pwm("D6", freq=1000, duty_u16=65535)  # PWM on the green LED, starting off
last = None  # the brightness last printed

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    clicks = min(max(knob.position(), 0), STEPS)  # keep it between 0 and STEPS
    knob.set_position(clicks)  # so turning back past the end responds straight away
    led.duty_u16(65535 - clicks * 65535 // STEPS)  # the off time, as the LED is on when low
    percent = clicks * 100 // STEPS
    if percent != last:
        print(percent, "%")
        last = percent
    time.sleep_ms(10)
