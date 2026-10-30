"""Stand-in for MicroPython's `machine` module, so phyduino.py and analog_shield.py run on a PC.

Records what the library does (pin set-up, SPI and I2C traffic) and lets a
test choose what the hardware returns. Copied from phyduino_pico_micropython's
tests/, with pin interrupts added (Pin.irq() and Pin.drive()).
"""


def reset():
    Pin.created.clear()
    Pin.levels.clear()
    Pin.handlers.clear()
    ADC.values.clear()
    SPI.instances.clear()
    I2C.instances.clear()
    I2C.devices.clear()
    UART.instances.clear()
    PWM.instances.clear()
    Timer.instances.clear()
    mem32.clear()


class Pin:
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    PULL_UP = 1
    PULL_DOWN = 2
    IRQ_FALLING = 4
    IRQ_RISING = 8

    created = []   # every Pin(...) call: (id, mode, pull, keyword arguments)
    levels = {}    # GPIO number -> level, shared by every Pin object for that GPIO
    handlers = {}  # GPIO number -> (Pin, handler, trigger, hard) from the last irq() call

    def __init__(self, id, mode=-1, pull=-1, **kwargs):
        self.id = id
        self.mode = mode
        self.pull = pull
        self.kwargs = kwargs
        Pin.created.append((id, mode, pull, kwargs))
        if "value" in kwargs:
            Pin.levels[id] = kwargs["value"]

    def value(self, level=None):
        if level is None:
            return Pin.levels.get(self.id, 0)
        Pin.levels[self.id] = 1 if level else 0

    __call__ = value

    def irq(self, handler=None, trigger=IRQ_FALLING | IRQ_RISING, hard=False):
        if handler is None:
            Pin.handlers.pop(self.id, None)
        else:
            Pin.handlers[self.id] = (self, handler, trigger, hard)

    @staticmethod
    def drive(id, level):
        """Test helper: the outside world sets a pin's level, running its interrupt on a matching edge."""
        old = Pin.levels.get(id, 0)
        Pin.levels[id] = 1 if level else 0
        if id in Pin.handlers and old != Pin.levels[id]:
            pin, handler, trigger, _ = Pin.handlers[id]
            if trigger & (Pin.IRQ_RISING if level else Pin.IRQ_FALLING):
                handler(pin)


class ADC:
    values = {}  # channel or GPIO -> 16-bit reading

    def __init__(self, id):
        self.id = id

    def read_u16(self):
        return ADC.values.get(self.id, 0)


class SPI:
    MSB = 0
    LSB = 1
    instances = []

    def __init__(self, id, **kwargs):
        self.id = id
        self.kwargs = kwargs
        self.writes = []     # each write() as a list of byte values
        self.responses = []  # bytes returned by successive read() calls
        SPI.instances.append(self)

    def write(self, data):
        self.writes.append(list(data))

    def read(self, count, write=0x00):
        data = self.responses.pop(0) if self.responses else bytes(count)
        assert len(data) == count, "test queued %d bytes, library read %d" % (len(data), count)
        return data


class I2C:
    instances = []
    devices = {}  # address -> bytearray(256) of registers

    def __init__(self, id, **kwargs):
        self.id = id
        self.kwargs = kwargs
        self.writes = []  # (address, register, list of byte values)
        I2C.instances.append(self)

    def _device(self, address):
        if address not in I2C.devices:
            raise OSError(19)  # ENODEV, as MicroPython raises on a NACK
        return I2C.devices[address]

    def readfrom_mem(self, address, register, count):
        return bytes(self._device(address)[register:register + count])

    def writeto_mem(self, address, register, data):
        regs = self._device(address)
        regs[register:register + len(data)] = data
        self.writes.append((address, register, list(data)))

    def scan(self):
        return sorted(I2C.devices) if self.id == 1 else []


class UART:
    instances = []

    def __init__(self, id, **kwargs):
        self.id = id
        self.kwargs = kwargs
        self.sent = b""
        UART.instances.append(self)

    def write(self, data):
        self.sent += data.encode() if isinstance(data, str) else bytes(data)
        return len(data)

    def read(self, count=None):
        return None  # nothing wired to RX


class PWM:
    instances = []

    def __init__(self, pin):
        self.pin = pin
        self.frequency = None
        self.duty = None
        PWM.instances.append(self)

    def freq(self, value=None):
        if value is None:
            return self.frequency
        self.frequency = value

    def duty_u16(self, value=None):
        if value is None:
            return self.duty
        self.duty = value


class Timer:
    ONE_SHOT = 0
    PERIODIC = 1
    instances = []

    def __init__(self, id=-1, mode=PERIODIC, period=-1, callback=None):
        self.mode = mode
        self.period = period
        self.callback = callback
        self.running = True
        Timer.instances.append(self)

    def deinit(self):
        self.running = False

    def fire(self):
        """Test helper: the period has passed."""
        if self.running:
            self.running = self.mode == Timer.PERIODIC
            self.callback(self)


class _Mem32(dict):
    """machine.mem32: 32-bit register reads and writes by address."""

    PAD_RESET = 0x56  # RP2040 PADS_BANK0 GPIOn reset value (DRIVE = 4 mA)

    def __getitem__(self, address):
        return self.get(address, self.PAD_RESET)


mem32 = _Mem32()
