def error(lcd, num):
    _list_error = [('ERROR: 0', 'limit switch 1', 'not pressed', ' '),
                   ('ERROR: 1', 'limit switch 2', 'not pressed', ' '),
                   ('ERROR: 2', 'bunker empty', 'fill up the material', ' '),
                   ('ERROR: 3', ' ', 'low oil level', ' '),
                   ('ERROR: 4', ' ', 'motor overheating', ' '),
                   ('ERROR: 5', 'emergence button', 'is pressed', ' ')]

    lcd.move_to(1, 0)
    lcd.putstr(_lcd_reload_display(_list_error[num][0]))
    lcd.move_to(0, 1)
    lcd.putstr(_lcd_reload_display(_list_error[num][1]))
    lcd.move_to(0, 2)
    lcd.putstr(_lcd_reload_display(_list_error[num][2]))
    lcd.move_to(0, 3)
    lcd.putstr(_lcd_reload_display(_list_error[num][3]))


def _lcd_reload_display(string):
    return string + (20 - len(string)) * ' '
