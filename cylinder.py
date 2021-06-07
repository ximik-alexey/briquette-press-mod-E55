
class Cylinder:
    def __init__(self, pin_1, pin_2):
        self.pin_1 = pin_1
        self.pin_2 = pin_2
        self.state = False

    def open_cylinder(self):
        self.pin_1.on()
        self.pin_2.off()
        self.state = True

    def close_cylinder(self):
        self.pin_1.off()
        self.pin_2.on()
        self.state = False

    def cylinder_timeout(self, param, time, utime):
        _t_ms = param * 1000
        if _t_ms > utime.ticks_ms() - time:
            del _t_ms
            return False
        else:
            return True
