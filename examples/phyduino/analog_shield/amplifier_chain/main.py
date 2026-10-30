# Prints the voltage at each stage of the temperature amplifier, once a
# second, as columns:
#   A1       the sensor's voltage, read directly
#   sensor   the sensor's voltage, worked out back from the amplifier's output
#   opamp    the amplifier's output (J8 pin 4), sensor * gain - offset
#   A3       the amplifier's output after the R14/R15 divider
#
# Needs analog_shield.py on the board, JP4 on 5 V, JP1 on INT and JP2 on EXT.
# Check the opamp column with a meter on J8 pin 4. With JP1 on EXT, the
# sensor on J1 is measured instead.

import time  # sleep() for pauses

import analog_shield as shield  # the Analog Shield library, used as shield.<name>
import phyduino as mcu  # the Phyduino Pico library, used as mcu.<name>

mcu.analog_averaging(16)  # average 16 samples per reading: steadier

print("gain %.3f, offset %.3f V" % (shield.amplifier_gain(), shield.amplifier_offset_volts()))
print("A1      sensor  opamp   A3")

while True:  # repeats until stopped: Interrupt in PyCharm, or mpremote soft-reset
    print("%.3f   %.3f   %.3f   %.3f" % (
        shield.raw_sensor_volts(),
        shield.sensor_volts(),
        shield.amplifier_volts(),
        shield.output_volts(),
    ))
    time.sleep(1)
