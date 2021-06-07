import json
import utime


class Setting:

    def __init__(self, lcd, b_plus, b_minus, b_set):
        self._change = False
        self.view = False
        self.settings = None
        self._number_setting = 0
        self._len_set = None
        self.lcd = lcd
        self.button_plus = b_plus
        self.button_minus = b_minus
        self.button_set = b_set
        self._pos_my_symbol = True
        self._timedelta = None
        self._name_list = ['first_limit_switch_time',
                           'second_limit_switch_time',
                           'third_cylinder_time_to_open',
                           'cycles_to_stops',
                           'heating_cycles']

    def _next_settings(self):
        if self.view and not self._change:
            if self._number_setting < self._len_set:
                self._number_setting += 1
            if self._number_setting == self._len_set:
                self._number_setting = 0
            self._display_setting()

    def _previous_settings(self):
        if self.view and not self._change:
            if self._number_setting >= 0:
                self._number_setting -= 1
            if self._number_setting < 0:
                self._number_setting = self._len_set - 1
            self._display_setting()

    def _display_setting(self):
        try:
            self.lcd.move_to(6, 0)
            self.lcd.putstr('SETTING')
            self.lcd.move_to(1, 1)
            _string_number_param = 'P0{}'.format(str(self._number_setting))
            self.lcd.putstr(_string_number_param + (20 - len(_string_number_param)) * ' ')
            self.lcd.move_to(1, 2)
            _string_value_param = 'VALUE: {}'.format(str(self.settings[self._number_setting][1]))
            self.lcd.putstr(_string_value_param + (20 - len(_string_value_param)) * ' ')
            del _string_value_param, _string_number_param
            if self.view and not self._change:
                self.lcd.move_to(0, 3)
                self.lcd.putstr(' ' * 20)
            if self.view and self._change:
                if self._pos_my_symbol:
                    self.lcd.move_to(1, 3)
                    self.lcd.putstr('EDIT->')
                    if self._timedelta is None:
                        self._timedelta = utime.ticks_ms()
                    if self.settings[self._number_setting][1] < 10:
                        self.lcd.move_to(10, 3)
                        self.lcd.putchar(chr(0))
                    else:
                        self.lcd.move_to(11, 3)
                        self.lcd.putchar(chr(0))
                    if (utime.ticks_ms() - self._timedelta) > 200:
                        self.lcd.move_to(1, 3)
                        self.lcd.putstr('EDIT->' + ' ' * 14)
                elif not self._pos_my_symbol:
                    self.lcd.move_to(1, 3)
                    self.lcd.putstr('EDIT->')
                    if self._timedelta is None:
                        self._timedelta = utime.ticks_ms()
                        if self.settings[self._number_setting][1] < 10:
                            self.lcd.move_to(8, 3)
                            self.lcd.putchar(chr(0))
                        else:
                            self.lcd.move_to(9, 3)
                            self.lcd.putchar(chr(0))
                    if (utime.ticks_ms() - self._timedelta) > 200:
                        self.lcd.move_to(1, 3)
                        self.lcd.putstr('EDIT->' + ' ' * 14)
                if (utime.ticks_ms() - self._timedelta) > 400:
                    del self._timedelta
                    self._timedelta = None
        except:
            return

    def _convert(self):
        _val_sec = int(self.settings[self._number_setting][1])
        _val_ms = round((self.settings[self._number_setting][1] - _val_sec) * 10, 0)
        if self._pos_my_symbol:
            if self.button_plus.get_time() > 0.15:
                _val_ms += 1
                if _val_ms > 9:
                    _val_ms = 0
            elif self.button_minus.get_time() > 0.15:
                _val_ms -= 1
                if _val_ms < 0:
                    _val_ms = 9
        if not self._pos_my_symbol:
            if self.button_plus.get_time() > 0.15:
                _val_sec += 1
                if _val_sec > 30:
                    _val_sec = 0
            if self.button_minus.get_time() > 0.15:
                _val_sec -= 1
                if _val_sec < 0:
                    _val_sec = 30
        self.settings[self._number_setting][1] = round(_val_sec + (_val_ms / 10), 1)
        del _val_sec, _val_ms

    def view_settings(self):
        if not self.view:
            self.view = True
        if self.view and not self._change:
            _time_button = self.button_set.get_time()
            if self.button_plus.get_time() > 0.15:
                self._next_settings()
            if self.button_minus.get_time() > 0.15:
                self._previous_settings()
            if 2 < _time_button < 4:
                self._change = True
            if _time_button > 5:
                self.view = False
            del _time_button
        if self.view and self._change:
            _time_button = self.button_set.get_time()
            if _time_button > 3:
                self._change = False
                self._pos_my_symbol = True
                self.save_settings()
                self.lcd.clear()
                return
            elif _time_button > 0.15 and self._pos_my_symbol:
                self._pos_my_symbol = False
            elif _time_button > 0.15 and not self._pos_my_symbol:
                self._pos_my_symbol = True
            self._convert()
            del _time_button
        self._display_setting()

    def load_settings(self):
        with open('settings.json', 'r') as file:
            _settings = json.loads(file.read())
        self.settings = [[i, _settings[i]] for i in self._name_list]
        # self.settings = [[key, value] for key, value in _settings.items()] # in micropython dict not ordered
        self._len_set = len(self.settings)
        del _settings, file

    def save_settings(self):
        _settings = {i[0]: i[1] for i in self.settings}
        with open('settings.json', 'w') as file:
            json.dump(_settings, file)
        del _settings, file

    def create_settings(self):
        self.settings = {i: 0.0 for i in self._name_list}
        with open('settings.json', 'w') as file:
            json.dump(self.settings, file)
        del file


if __name__ == '__main__':
    set = Setting(None, None, None, None)
    set.create_settings()
