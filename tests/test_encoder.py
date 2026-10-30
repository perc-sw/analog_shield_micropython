"""The rotary encoder: quadrature counting from pin interrupts, and its push switch."""

import pytest

# From the Rev C PCB netlist: ENC_SW on D2, ENC_A on D3, ENC_B on D4.
SW, A, B = 6, 7, 8  # GPIO

# (A, B) through one click clockwise, starting and ending at rest (both pulled high)
CLOCKWISE = [(0, 1), (0, 0), (1, 0), (1, 1)]
ANTICLOCKWISE = [(1, 0), (0, 0), (0, 1), (1, 1)]


@pytest.fixture
def knob(shield, fake):
    fake.Pin.levels.update({SW: 1, A: 1, B: 1})  # pull-ups: at rest, not pressed
    return shield.encoder()


def turn(fake, sequence, clicks=1):
    for _ in range(clicks):
        for a, b in sequence:
            fake.Pin.drive(A, a)
            fake.Pin.drive(B, b)


def test_pins_are_inputs_without_pulls(knob, fake):
    for gpio in (SW, A, B):
        assert (gpio, fake.Pin.IN, None, {}) in fake.Pin.created
    both = fake.Pin.IRQ_RISING | fake.Pin.IRQ_FALLING
    assert fake.Pin.handlers[A][2:] == (both, True) and fake.Pin.handlers[B][2:] == (both, True)
    assert SW not in fake.Pin.handlers  # until on_press()


def test_encoder_is_one_object(shield, knob):
    assert shield.encoder() is knob


def test_starts_at_zero(knob):
    assert knob.position() == 0 and knob.steps() == 0


def test_clockwise_counts_up_one_per_click(knob, fake):
    turn(fake, CLOCKWISE, 3)
    assert knob.position() == 3
    assert knob.steps() == 12


def test_anticlockwise_counts_down(knob, fake):
    turn(fake, ANTICLOCKWISE, 2)
    assert knob.position() == -2


def test_back_and_forth_returns_to_zero(knob, fake):
    turn(fake, CLOCKWISE, 5)
    turn(fake, ANTICLOCKWISE, 5)
    assert knob.position() == 0


def test_bounce_on_one_line_cancels_out(knob, fake):
    for level in (0, 1, 0, 1, 0):  # A chatters before settling low
        fake.Pin.drive(A, level)
    fake.Pin.drive(B, 0)
    fake.Pin.drive(A, 1)
    fake.Pin.drive(B, 1)
    assert knob.steps() == 4 and knob.position() == 1


def test_skipped_state_does_not_count(knob, fake):
    fake.Pin.levels.update({A: 0, B: 0})  # both changed before the interrupt ran
    fake.Pin.handlers[A][1](fake.Pin.handlers[A][0])
    assert knob.steps() == 0


def test_part_turn_rounds_down(knob, fake):
    turn(fake, CLOCKWISE[:2])
    assert knob.position() == 0
    turn(fake, ANTICLOCKWISE[2:])  # back to rest the other way: (0, 1) then (1, 1)
    assert knob.position() == 0


def test_set_position(knob, fake):
    turn(fake, CLOCKWISE, 4)
    knob.set_position()
    assert knob.position() == 0
    knob.set_position(10)
    turn(fake, ANTICLOCKWISE)
    assert knob.position() == 9


def test_pressed_reads_the_switch(knob, fake):
    assert not knob.pressed()
    fake.Pin.drive(SW, 0)
    assert knob.pressed()


def test_on_press_calls_back_once_per_press(knob, fake, fake_clock):
    presses = []
    knob.on_press(lambda: presses.append(1))
    assert fake.Pin.handlers[SW][2] == fake.Pin.IRQ_FALLING
    fake.Pin.drive(SW, 0)
    assert presses == [1]
    fake.Pin.drive(SW, 1)  # release: rising edge, ignored
    assert presses == [1]


def test_on_press_ignores_bounce(knob, fake, fake_clock):
    presses = []
    knob.on_press(lambda: presses.append(1))
    fake.Pin.drive(SW, 0)
    fake_clock.sleep_ms(5)
    fake.Pin.drive(SW, 1)
    fake.Pin.drive(SW, 0)  # 5 ms later: bounce
    assert len(presses) == 1
    fake_clock.sleep_ms(100)
    fake.Pin.drive(SW, 1)
    fake.Pin.drive(SW, 0)  # a second press
    assert len(presses) == 2


def test_on_press_none_stops(knob, fake):
    presses = []
    knob.on_press(lambda: presses.append(1))
    knob.on_press(None)
    assert SW not in fake.Pin.handlers
    fake.Pin.drive(SW, 0)
    assert presses == []
