import utime
from setting import Setting
from error import error
import json


class Work:

    def __init__(self, lcd, b_plus, b_minus, b_set,
                 b_start, b_stop, lim_sw_1, lim_sw_2,
                 cyl_1, cyl_2, motor, emergency, press):
        self.lcd = lcd  # lcd 20x4 i2c
        self._run = False
        self._error = False
        self._num_error = None
        self._critical_error = False
        self._pause = True
        self._setting = False
        self._timedelta = None
        self.button_plus = b_plus
        self.button_minus = b_minus
        self.button_set = b_set
        self.motor = motor
        self.button_start = b_start
        self.button_stop = b_stop
        self.limit_switch_1 = lim_sw_1
        self.limit_switch_2 = lim_sw_2
        self.cylinder_1 = cyl_1
        self.cylinder_2 = cyl_2
        self.pressure = press
        self.emergency = emergency
        self.thermal_relay = None
        self.button_emergency = None
        self.quantity_cycles = None
        self._oil_is_heated = False
        self.setting_obj = None
        self.parametrs = None
        self.cycles = None
        self.cycle_state = 0

    def run(self):

        if self._error:  # режим ошибок
            self.motor.off()
            error(self.lcd, self._num_error)
            if not self.emergency.emergency_state and not self._critical_error:
                self._error = False
                self._pause = True
                self.lcd.clear()

        elif self._pause:  # режим паузы
            if self.emergency.emergency_state:
                self._error_in_cycle(self.emergency.emergency_number)
            if self._timedelta is None:
                self._start_timedelta()
            if self._get_timedelta() > 400:
                self.lcd.move_to(5, 1)
                self.lcd.putstr('PRESS RUN')
                self.lcd.move_to(5, 2)
                self.lcd.putstr('FOR START')
            if self._get_timedelta() > 1300:
                self.lcd.clear()
                self._clear_timedelta()
            if self.button_set.get_time() > 3:
                self.lcd.clear()
                self._setting = True
                self._pause = False
            if self.button_start.get_time() > 0.15:
                self._pause = False
                self._run = True
                del self.parametrs
                self.parametrs = None
                self._clear_timedelta()
                self.lcd.clear()

        elif self._setting:  # режим настроек
            if not self.setting_obj:
                self.setting_obj = Setting(self.lcd, self.button_plus, self.button_minus, self.button_set)
                self.setting_obj.load_settings()
            if self.setting_obj:
                self.setting_obj.view_settings()
            if not self.setting_obj.view:
                self._setting = False
                self._pause = True
                self.lcd.clear()
                del self.setting_obj
                self.setting_obj = None

        elif self._run:  # режим работы
            if self.emergency.emergency_state:
                if self.emergency.emergency_number == 2 and self.cycle_state == 1:
                    self.emergency.emergency_bunker = True
                    self.cycle_state = 2
                    self.cycles = int(self.parametrs['cycles_to_stops'])
                else:
                    self._error_in_cycle(self.emergency.emergency_number)
            if not self.parametrs:
                self._load_parametr()
            if not self.motor.state:
                self.motor.on()
            if self.cycle_state == 1:
                self._work_cycle()
            elif self.cycle_state == 0:
                if self.cycles is None:
                    self.cycles = int(self.parametrs['heating_cycles'])
                self._heating_oil_cycle()
            elif self.cycle_state == 2:
                self._stop_cycle()
            if self.button_stop.get_time() > 0.15:
                self.cycles = int(self.parametrs['cycles_to_stops'])
                self.cycle_state = 2

    def _work_cycle(self, cyl_2=True):
        self._cycle(cyl_2)
        if not self._error:
            self._display_cycles()

    def _heating_oil_cycle(self, cyl_2=False):
        if self.cycles == 0:
            self._oil_is_heated = True
            self.cycle_state = 1
            self.lcd.clear()
        else:
            self._cycle(cyl_2)
            if not self._error:
                self._display_cycles()

    def _stop_cycle(self, cyl_2=False):
        if self.cycles == 0:
            self.motor.off()
            self._run = False
            self._pause = True
            self.cycles = None
            self.cycle_state = 0
            self.emergency.emergency_bunker = False
            self.lcd.clear()
        else:
            self._cycle(cyl_2)
            if not self._error:
                self._display_cycles()

    def _cycle(self, cylinder_2_work_on):
        if self._timedelta is None:
            self._start_timedelta()
        if not self.cylinder_1.state:
            self.cylinder_1.close_cylinder()
            if self.cylinder_1.cylinder_timeout(self.parametrs['first_limit_switch_time'], self._timedelta, utime):
                self._error_in_cycle(0)
                return
            if self.limit_switch_1.state_pin:
                if not cylinder_2_work_on:
                    self.cylinder_2.on()
                if cylinder_2_work_on:
                    self.cylinder_2.off()
                self.cylinder_1.open_cylinder()
                self._clear_timedelta()
                self._start_timedelta()

        if self.cylinder_1.state:
            if cylinder_2_work_on:
                if self._get_timedelta() > (int(self.parametrs['third_cylinder_time_to_open'] * 1000)):
                    self.cylinder_2.on()
                elif self.pressure.state_pin:
                    self.cylinder_2.on()
            if self.cylinder_1.cylinder_timeout(self.parametrs['second_limit_switch_time'], self._timedelta, utime):
                self._error_in_cycle(1)
                return
            if self.limit_switch_2.state_pin:
                self.cylinder_1.close_cylinder()
                self._clear_timedelta()
                if cylinder_2_work_on:
                    self.cycles += 1
                else:
                    self.cycles -= 1

    def _error_in_cycle(self, num_error):
        self.motor.off()
        self._run = False
        self._error = True
        self._num_error = num_error
        self.lcd.clear()
        if self._num_error == 0 or self._num_error == 1:
            self._critical_error = True

    def _param_converter(self, param):
        _t_ms = param * 1000
        if _t_ms > utime.ticks_ms() - self._timedelta:
            del _t_ms
            return True
        else:
            del _t_ms
            return False

    def _check_emergency(self):
        pass

    def _clear_timedelta(self):
        del self._timedelta
        self._timedelta = None

    def _start_timedelta(self):
        self._timedelta = utime.ticks_ms()

    def _get_timedelta(self):
        return utime.ticks_ms() - self._timedelta

    def _load_parametr(self):
        with open('settings.json', 'r') as file:
            self.parametrs = json.loads(file.read())
        del file

    def _display_cycles(self):
        self.lcd.move_to(1, 1)
        if self.cycle_state == 0:
            self.lcd.putstr('HEATING')
        elif self.cycle_state == 1:
            self.lcd.putstr('WORK')
        elif self.cycle_state == 2:
            self.lcd.putstr('STOP')
        self.lcd.move_to(1, 3)
        _string_number_param = 'CYCLES: {}'.format(str(self.cycles))
        self.lcd.putstr(_string_number_param + (19 - len(_string_number_param)) * ' ')
        del _string_number_param
