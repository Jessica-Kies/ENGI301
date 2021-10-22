# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
PocketBeagle Arcade Machine
---------------------------------------------------------------------------
License:   
Copyright 2017 Octavo Systems, LLC

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
Arcade Machine

  Please see README.txt for overview and how to run the game.
  
  Please use run_arcade_machine.sh for instructions to auto-run the game at 
boot

"""
import os
import random
import time

import Adafruit_BBIO.PWM as PWM

# ------------------------------------------------------------------------
# Global Constants
# ------------------------------------------------------------------------

# HT16K33 values
DISPLAY_I2C_BUS              = 1                 # I2C 1  
DISPLAY_I2C_ADDR             = 0x70
DISPLAY_CMD                  = "/usr/sbin/i2cset -y 1 0x70"         

# Peripheral path
GPIO_BASE_PATH               = "/sys/class/gpio"
ADC_BASE_PATH                = "/sys/bus/iio/devices/iio:device0"

# GPIO direction
IN                           = True
OUT                          = False

# GPIO output state
LOW                          = "0"
HIGH                         = "1"

# Button GPIO values
BUTTON0                      = (1, 14)           # gpio46 / P2_22
BUTTON1                      = (1, 12)           # gpio44 / P2_24
BUTTON2                      = (1, 15)           # gpio47 / P2_18
BUTTON3                      = (2, 0)            # gpio64 / P2_20
BUTTONS                      = [BUTTON0, BUTTON1, BUTTON2, BUTTON3]

# LED GPIO values
LED0                         = (1, 27)           # gpio59 / P2_2
LED1                         = (1, 26)           # gpio58 / P2_4 
LED2                         = (1, 25)           # gpio57 / P2_6
LED3                         = (1, 28)           # gpio60 / P2_8
LEDS                         = [LED0, LED1, LED2, LED3]
  
# Buzzer GPIO value
BUZZER                       = "P2_1"           # gpio50 / (1, 18)

NOTES                        =  [262, 329, 392, 529]

# ------------------------------------------------------------------------
# GPIO/ADC access library
# ------------------------------------------------------------------------

def gpio_setup(gpio, direction, default_value=False):
    """Setup GPIO pin
    
      * Test if GPIO exists; if not create it
      * Set direction
      * Set default value
    """
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    if not os.path.exists(path):
        # "echo {gpio_number} > {GPIO_BASE_PATH}/export"
        print("Create GPIO: {0}".format(gpio_number))
        with open("{0}/export".format(GPIO_BASE_PATH), 'w') as f:
            f.write(gpio_number)
    
    if direction:
        # "echo in > {path}/direction"
        with open("{0}/direction".format(path), 'w') as f:
            f.write("in")
    else:
        # "echo out > {path}/direction"
        with open("{0}/direction".format(path), 'w') as f:
            f.write("out")
        
    if default_value:
        # "echo {default_value} > {path}/value"
        with open("{0}/value".format(path), 'w') as f:
            f.write(default_value)
    
# End def


def gpio_set(gpio, value):
    """Set GPIO ouptut value."""
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    # "echo {value} > {path}/value"
    with open("{0}/value".format(path), 'w') as f:
        f.write(value)

# End def


def gpio_get(gpio):
    """Get GPIO input value."""
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    # "cat {path}/value"
    with open("{0}/value".format(path), 'r') as f:
        out = f.read()
    
    return float(out)

# End def


def adc_get(channel):
    """Get ADC input value.
    
    Returns:
        value (float):  Value will be between 0 (0V) and 1.0 (1.8V)."""
    with open("{0}/{1}".format(ADC_BASE_PATH, channel), 'r') as f:
        out = f.read()
    
    return float(float(out) / float(4096))

# End def

# ------------------------------------------------------------------------
# Display Code
# ------------------------------------------------------------------------
HEX_DIGITS                  = [0x3f, 0x06, 0x5b, 0x4f,    # 0, 1, 2, 3
                               0x66, 0x6d, 0x7d, 0x07,    # 4, 5, 6, 7
                               0x7f, 0x6f, 0x77, 0x7c,    # 8, 9, A, b
                               0x39, 0x5e, 0x79, 0x71]    # C, d, E, F

CLEAR_DIGIT                 = 0x7F
POINT_VALUE                 = 0x80

DIGIT_ADDR                  = [0x00, 0x02, 0x06, 0x08]
COLON_ADDR                  = 0x04
                      
HT16K33_BLINK_CMD           = 0x80
HT16K33_BLINK_DISPLAYON     = 0x01
HT16K33_BLINK_OFF           = 0x00
HT16K33_BLINK_2HZ           = 0x02
HT16K33_BLINK_1HZ           = 0x04
HT16K33_BLINK_HALFHZ        = 0x06

HT16K33_SYSTEM_SETUP        = 0x20
HT16K33_OSCILLATOR          = 0x01

HT16K33_BRIGHTNESS_CMD      = 0xE0
HT16K33_BRIGHTNESS_HIGHEST  = 0x0F
HT16K33_BRIGHTNESS_DARKEST  = 0x00

def display_setup():
    """Setup display"""
    # i2cset -y 0 0x70 0x21
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_SYSTEM_SETUP | HT16K33_OSCILLATOR)))
    # i2cset -y 0 0x70 0x81
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_BLINK_CMD | HT16K33_BLINK_OFF | HT16K33_BLINK_DISPLAYON)))
    # i2cset -y 0 0x70 0xEF
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_BRIGHTNESS_CMD | HT16K33_BRIGHTNESS_HIGHEST)))

# End def


def display_clear():
    """Clear the display to read '0000'"""
    # i2cset -y 0 0x70 0x00 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[0], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x02 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[1], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x06 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[2], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x08 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[3], HEX_DIGITS[0]))
    
    os.system("{0} {1} {2}".format(DISPLAY_CMD, COLON_ADDR, 0x0))
    
# End def


def display_encode(data, double_point=False):
    """Encode data to TM1637 format.
    
    This function will convert the data from decimal to the TM1637 data fromt
    
    :param value: Value must be between 0 and 15
    
    Will throw a ValueError if number is not between 0 and 15.
    """
    ret_val = 0
    
    try:
        if (data != CLEAR_DIGIT):
            if double_point:
                ret_val = HEX_DIGITS[data] + POINT_VALUE
            else:
                ret_val = HEX_DIGITS[data]
    except:
        raise ValueError("Digit value must be between 0 and 15.")

    return ret_val

# End def


def display_set(data):
    """Display the data.
    
    data is a list containing 4 values
    """
    for i in range(0,3):
        display_set_digit(i, data[i])
    
# End def


def display_set_digit(digit_number, data, double_point=False):
    """Update the given digit of the display."""
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[digit_number], display_encode(data, double_point)))    

# End def


def update_display(value):
    """Update the value on the display.  
    
    This function will clear the display and then set the appropriate digits
    
    :param value: Value must be between 0 and 9999.
    
    Will throw a ValueError if number is not between 0 and 9999.
    """  
    """
    if (value < 0) or (value > 9999):
       raise ValueError("Value is not within 0 and 9999.") 
    
    if (value < 10):
        display_set_digit(3, value)
        display_set_digit(2, 0)
        display_set_digit(1, 0)
        display_set_digit(0, 0)
    else:
        if (value < 100):
            display_set_digit(3, value % 10)
            display_set_digit(2, value / 10)
            display_set_digit(1, 0)
            display_set_digit(0, 0)
    
    """
    for i in range(0,4):
        display_set_digit((3 - i), (value % 10))
        value = (value / 10)
    #"""
    #pass
    

# End def
    
def setup_game():
    "Setup the buttons for the game"
    
    gpio_setup(BUTTON0, IN)
    gpio_setup(BUTTON1, IN)
    gpio_setup(BUTTON2, IN)
    gpio_setup(BUTTON3, IN)    

    gpio_setup(LED0, OUT, LOW)
    gpio_setup(LED1, OUT, LOW)
    gpio_setup(LED2, OUT, LOW)
    gpio_setup(LED3, OUT, LOW)
    
    #gpio_setup(BUZZER, OUT, LOW)
        
    display_setup

# ------------------------------------------------------------------------
# Piezo Buzzer Code
# ------------------------------------------------------------------------

def play_note(note, sec):
    PWM.start(BUZZER, 50, note)
    time.sleep(sec)

# ------------------------------------------------------------------------
# Game Code
# ------------------------------------------------------------------------

def play_game():
    pattern = []
    user_input = []
    score = 0
    playing_game = True
    
    gpio_set(LED0, LOW) 
    gpio_set(LED1, LOW)
    gpio_set(LED2, LOW)
    gpio_set(LED3, LOW) 
    
    time.sleep(1)
    
    
    for x in range(7):
       rand = random.randint(0, 3)
       pattern.append(rand)
    print(pattern)
    
    for i in range(0, len(pattern)):
        gpio_set(LEDS[pattern[i]], HIGH)
        time.sleep(0.5)
        gpio_set(LEDS[pattern[i]], LOW)
        time.sleep(0.5)
        
    while (len(user_input) < len(pattern)):   # Wait until any button is pressed
        if (gpio_get(BUTTON0) == 0):
            gpio_set(LED0, HIGH)
            time.sleep(.5)
            user_input.append(0)
            gpio_set(LED0, LOW)
            print("Button 0 accepts input") # TESTING 
        elif (gpio_get(BUTTON1) == 0):
            gpio_set(LED1, HIGH)
            time.sleep(.5)
            user_input.append(1)
            gpio_set(LED1, LOW)
            print("Button 1 accepts input") # TESTING 
        elif (gpio_get(BUTTON2) == 0): #Solved - Add SSH script (config-pin P2_18 gpio)
            gpio_set(LED2, HIGH)
            time.sleep(.5)
            user_input.append(2)
            gpio_set(LED2, LOW)
            print("Button 2 accepts input") # TESTING 
        elif (gpio_get(BUTTON3) == 0):
            gpio_set(LED3, HIGH)
            time.sleep(.5)
            user_input.append(3)
            gpio_set(LED3, LOW)
            print("Button 3 accepts input") # TESTING
    if (pattern == user_input):
        print("win")
    elif (pattern != user_input):
        print("lose")
    
    


# End def
    
# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------
        
if __name__ == '__main__':
    display_setup()
    display_clear()
    
    setup_game()
    
    
    playing = True
    
    play_game()