from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd


def init_display():
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 4
    I2C_NUM_COLS = 20
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    lcd.clear()
    _my_symbol = [0x04, 0x0E, 0x1F, 0x04, 0x04, 0x04, 0x00, 0x00]
    lcd.custom_char(0, _my_symbol)
    return lcd
