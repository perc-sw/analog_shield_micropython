# Prints the shield's readings four times a second as label:value pairs, for a
# serial plotter: the temperature from the raw sensor (A1) and through the
# amplifier, the encoder position, the selected channel (0 or 3), the pot and
# VBUS voltages. The Phyduino's LED blinks while it runs.
#
# Needs analog_shield.py on the board, JP3 (VIO) on 3.3 V, JP4 on 5 V and JP1
# on INT (the on-board sensor). Starts reading the amplifier on A0 (JP2 on INT).
# Pressing the knob switches between A0 and A3: it only tells the code where
# JP2 is, so move JP2 to match (A3 is JP2 on EXT). Green LED: A0, red LED: A3,
# both on: the A3 ADC did not respond (until the next press).
#
# The two temperatures should agree to within about 3 C. The raw sensor line is
# coarser and noisier, as the RP2040's ADC reads A1 with no amplifier.

import analog_shield as shield
import phyduino as mcu
import time

_channel = "A0"

def channel_select():
    """Event handler for Encoder switch press."""
    global _channel
    _channel = "A3" if _channel == "A0" else "A0"
    shield.set_output_pin(_channel)
    shield.green_led.value(_channel == "A0")
    shield.red_led.value(_channel == "A3")


# Set up board before entering loop
Knob = shield.encoder()

shield.green_led.on()
shield.red_led.off()
shield.set_output_pin("A0")

Knob.on_press(channel_select)     # Set up event handler for button press
BuiltinLed = mcu.Led()
BuiltinLed.on()

while True:
    BuiltinLed.toggle()

    try:
        AmpTemperature = shield.temperature()
    except OSError:                 # External ADC did not respond.
        shield.green_led.on()       # indicate error has occurred.
        shield.red_led.on()
        time.sleep(0.25)
        continue

    EncoderCount = Knob.position()
    PotVoltage = shield.pot_volts()
    RawSensor = shield.temperature_from_volts(shield.raw_sensor_volts())
    VBusVoltage = mcu.vbus_volts()
    SelectedChannel = 0 if _channel == "A0" else 3

    print("Sensor:%.1f,Temp:%.1f,EncPosition:%d,Channel:%d,Pot:%.3f,Vbus:%.2f"
          % (RawSensor, AmpTemperature, EncoderCount, SelectedChannel, PotVoltage, VBusVoltage))

    time.sleep(0.25)