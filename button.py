import utime


class Button:
    def __init__(self, pin):
        self.push = False
        self.start_push_button_datetime = None
        self.push_time = None
        self.pin_state = pin

    def state(self):
        if self.pin_state.value() == 1 and not self.push:
            self.push = True
            self.start_push_button_datetime = utime.ticks_ms()
            self.push_time = None
        if self.push and self.pin_state.value() == 0:
            _period = utime.ticks_ms() - self.start_push_button_datetime
            self.push_time = round(_period / 1000, 1)
            self.start_push_button_datetime = None
            self.push = False
            del _period

    def get_time(self):
        if not self.push_time:
            return 0
        _time = self.push_time
        self.push_time = None
        return _time


class LimitSwitch:

    def __init__(self, pin):
        self.pin = pin
        self.state_pin = False

    def state(self):
        self.state_pin = True if self.pin.value() == 1 else False


class Emergency:
    def __init__(self, pin_button, pin_oil, pin_motor, pin_material):
        self.pin_button = pin_button
        self.pin_oil = pin_oil
        self.pin_motor = pin_motor
        self.pin_material = pin_material
        self.emergency_state = False
        self.emergency_number = None
        self.emergency_bunker = False

    def state(self):

        if self.pin_oil.value() == 0:
            self.emergency_state = True
            self.emergency_number = 3
        elif self.pin_motor.value() == 0:
            self.emergency_state = True
            self.emergency_number = 4
        elif self.pin_button.value() == 0:
            self.emergency_state = True
            self.emergency_number = 5
        elif self.pin_material.value() == 0:
            self.emergency_number = 2
            if self.emergency_bunker:
                self.emergency_state = False
            else:
                self.emergency_state = True
        else:
            self.emergency_state = False
            self.emergency_bunker = False

