#!/usr/bin/python3
# -*- coding: utf-8 -*-
import smbus
import time

import spidev as SPI
import SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration for OLED
RST = 19
# Note the following are only used with SPI
DC = 16
busSPI = 0
device = 0

# Raspberry Pi pin configuration for DS3231
address = 0x68
register = 0x00
# sec min hour week day mout year
NowTime = [0x00, 0x12, 0x16, 0x03, 0x28, 0x06, 0x17]
#w = ["SUN", "Mon", "Tues", "Wed", "Thur", "Fri", "Sat"]
w = ["ВСК", "ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
# /dev/i2c-1
bus = smbus.SMBus(1)


def ds3231SetTime():
    bus.write_i2c_block_data(address, register, NowTime)


def ds3231ReadTime():
    return bus.read_i2c_block_data(address, register, 7)


# 128x64 display with hardware SPI:
disp = SSD1306.SSD1306(RST, DC, SPI.SpiDev(busSPI, device))

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding_v = 16
padding_h = 1
top = padding_v
x = padding_h
fh = 24

t = ds3231ReadTime()
t[3] = t[3] & 0x07  # week
t[4] = t[4] & 0x3F  # day
t[5] = t[5] & 0x1F  # mouth

weekday = '{:^17}'.format(w[t[3] - 1])

font = ImageFont.truetype('fonts/Minecraftia-Regular.ttf', 14)
draw.text((5, 0), weekday, font=font, fill=255)

datestr = '{:02x}.{:02x}.20{:02x}'.format(t[4], t[5], t[6])
draw.text((19, top), datestr, font=font, fill=255)

font = ImageFont.truetype('fonts/Minecraftia-Regular.ttf', 18)

# ds3231SetTime()
while 1:
    t = ds3231ReadTime()
    t[0] = t[0] & 0x7F  # sec
    t[1] = t[1] & 0x7F  # min
    t[2] = t[2] & 0x3F  # hour
    t[3] = t[3] & 0x07  # week
    t[4] = t[4] & 0x3F  # day
    t[5] = t[5] & 0x1F  # mouth
    print("20%x/%02x/%02x %02x:%02x:%02x %s" % (t[6], t[5], t[4], t[2], t[1], t[0], w[t[3] - 1]))
    # Write time to disp
    timestr = '{:02x}:{:02x}:{:02x}'.format(t[2], t[1], t[0])
    draw.rectangle((0, top+ fh, width-x, height - 1), outline=1, fill=0)
    draw.text((20, top + fh), timestr, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(1)
