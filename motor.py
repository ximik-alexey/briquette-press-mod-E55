class Motor:
    def __init__(self, pin):
        self.pin = pin
        self.state = False

    def on(self):
        self.pin.high()
        self.state = True if self.pin.value() == 1 else False

    def off(self):
        self.pin.low()
        self.state = True if self.pin.value() == 1 else False

