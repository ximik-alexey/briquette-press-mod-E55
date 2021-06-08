import _thread
import utime
from button import Emergency, Button, LimitSwitch
import display
from machine import Pin
import machine
from work import Work
from cylinder import Cylinder
from motor import Motor

machine.freq(250000000)  # 250Mhz
button_set = Button(Pin(16, Pin.IN, Pin.PULL_DOWN))
button_plus = Button(Pin(17, Pin.IN, Pin.PULL_DOWN))
button_minus = Button(Pin(18, Pin.IN, Pin.PULL_DOWN))
button_start = Button(Pin(19, Pin.IN, Pin.PULL_DOWN))
button_stop = Button(Pin(20, Pin.IN, Pin.PULL_DOWN))
lim_sw_1 = LimitSwitch(Pin(21, Pin.IN, Pin.PULL_DOWN))
lim_sw_2 = LimitSwitch(Pin(22, Pin.IN, Pin.PULL_DOWN))
cylinder_1 = Cylinder(Pin(14, Pin.OUT, Pin.PULL_DOWN), Pin(12, Pin.OUT, Pin.PULL_DOWN))
cylinder_2 = Pin(15, Pin.OUT, Pin.PULL_DOWN)  # 380 pin in machine
pressure = LimitSwitch(Pin(6, Pin.IN, Pin.PULL_DOWN))
emergency = Emergency(Pin(10, Pin.IN, Pin.PULL_DOWN), Pin(8, Pin.IN, Pin.PULL_DOWN),
                      Pin(9, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN))
motor = Motor(Pin(13, Pin.OUT, Pin.PULL_DOWN))
lcd = display.init_display()

def input_thread():
    while True:
        button_set.state()
        button_plus.state()
        button_minus.state()
        button_start.state()
        button_stop.state()
        lim_sw_1.state()
        lim_sw_2.state()
        pressure.state()
        emergency.state()
        utime.sleep_ms(20)


_thread.start_new_thread(input_thread, ())

work = Work(lcd, button_plus, button_minus, button_set, button_start, button_stop,
            lim_sw_1, lim_sw_2, cylinder_1, cylinder_2, motor, emergency, pressure)

while True:
    work.run()
