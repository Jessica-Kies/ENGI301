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
import sys

import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO

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
BUTTON0                      = "P2_22"           # gpio46
BUTTON1                      = "P2_24"           # gpio44
BUTTON2                      = "P2_18"           # gpio47
BUTTON3                      = "P2_20"            # gpio64
BUTTONS                      = [BUTTON0, BUTTON1, BUTTON2, BUTTON3]

# LED GPIO values
LED0                         = "P2_2"          # gpio59
LED1                         = "P2_4"          # gpio58
LED2                         = "P2_6"           # gpio57
LED3                         = "P2_8"           # gpio60
LEDS                         = [LED0, LED1, LED2, LED3]
  
# Buzzer GPIO value
BUZZER                       = "P2_1"           # gpio50

SERVO                       = "P1_36"

NOTES                        =  [262, 329, 392, 529]

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
    """This function sets the buttons to read inputs. The LEDs are set to output 
    and initially be off"""
    
    GPIO.setup(BUTTON0, GPIO.IN)
    GPIO.setup(BUTTON1, GPIO.IN)
    GPIO.setup(BUTTON2, GPIO.IN)
    GPIO.setup(BUTTON3, GPIO.IN)    

    GPIO.setup(LED0, GPIO.OUT, GPIO.LOW) 
    GPIO.setup(LED1, GPIO.OUT, GPIO.LOW)
    GPIO.setup(LED2, GPIO.OUT, GPIO.LOW)
    GPIO.setup(LED3, GPIO.OUT, GPIO.LOW)
        
    display_setup
    
    global win_time
    win_time = 0
    global again_time
    again_time = 30
    
    return win_time, again_time
    
    

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
    playing_game = True
    global win_time
    global again_time
    
    GPIO.output(LED0, GPIO.LOW) 
    GPIO.output(LED1, GPIO.LOW)
    GPIO.output(LED2, GPIO.LOW)
    GPIO.output(LED3, GPIO.LOW)

    #win_time, again_time = setup_game()

    time.sleep(1)
    
    if again_time - win_time <= 5:
        a = 5   
    elif again_time - win_time <= 10:
        a = 4
    elif again_time - win_time <= 15:
        a = 3
    elif again_time - win_time <= 20:
        a = 2
    else:
        a = 1
        
    
    for x in range(a):
        rand = random.randint(0, 3)
        pattern.append(rand)
    print(pattern)
    
    for i in range(0, len(pattern)):
        GPIO.output(LEDS[pattern[i]], GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LEDS[pattern[i]], GPIO.LOW)
        time.sleep(0.5)
        
    while (len(user_input) < len(pattern)):   # Wait until any button is pressed
        if (GPIO.input(BUTTON0) == 0):
            GPIO.output(LED0, GPIO.HIGH)
            time.sleep(.5)
            user_input.append(0)
            GPIO.output(LED0, GPIO.LOW)
            print("Button 0 accepts input") # TESTING 
        elif (GPIO.input(BUTTON1) == 0):
            GPIO.output(LED1, GPIO.HIGH)
            time.sleep(.5)
            user_input.append(1)
            GPIO.output(LED1, GPIO.LOW)
            print("Button 1 accepts input") # TESTING 
        elif (GPIO.input(BUTTON2) == 0): #Solved - Add SSH script (config-pin P2_18 gpio)
            GPIO.output(LED2, GPIO.HIGH)
            time.sleep(.5)
            user_input.append(2)
            GPIO.output(LED2, GPIO.LOW)
            print("Button 2 accepts input") # TESTING 
        elif (GPIO.input(BUTTON3) == 0):
            GPIO.output(LED3, GPIO.HIGH)
            time.sleep(.5)
            user_input.append(3)
            GPIO.output(LED3, GPIO.LOW)
            print("Button 3 accepts input") # TESTING
    if (pattern == user_input):
        print("win")
        PWM.start(SERVO, 10)
        time.sleep(1)
        PWM.stop(SERVO)
        win_time = time.time()
        print(win_time)
        while(GPIO.input(BUTTON2) == 1):
            time.sleep(0.1)
            if (time.time() - win_time <= 5):
                print("LVL5")
            elif (time.time() - win_time <= 10):
                print ('LVL4')
            elif (time.time() - win_time <= 15):
                print ('LVL3')
            elif (time.time() - win_time <= 20):
                print ('LVL2')
            elif (time.time() - win_time <= 25):
                print ('LVL1')
            else:
                clear_game()
        if (GPIO.input(BUTTON2) == 0):
            again_time = time.time()
            print(again_time)
            play_game()
        #print(button_press_time)
    elif (pattern != user_input):
        global lose_time
        lose_time = time.time()
        print("lose")
        lock_game()
        

# End def

def clear_game():
    GPIO.output(LED0, GPIO.LOW) 
    GPIO.output(LED1, GPIO.LOW)
    GPIO.output(LED2, GPIO.LOW)
    GPIO.output(LED3, GPIO.LOW)
    print("off")
    sys.exit()
    
def lock_game():
    global lose_time
    while (time.time() - lose_time <= 5):
        print ("LOCK")
    while(GPIO.input(BUTTON2) == 1):
        time.sleep(0.1)
        if (GPIO.input(BUTTON2) == 0):
            play_game()
        elif (time.time() - lose_time >= 10):
            clear_game()
# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------
        
if __name__ == '__main__':
    #display_setup()
    #display_clear()
    
    setup_game()
    
    playing = True
    
    play_game()