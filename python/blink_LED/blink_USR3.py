"""
--------------------------------------------------------------------------
Blink_USR3
--------------------------------------------------------------------------
License:   
Copyright 2021 Jessica Kies

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

Program that will:
    Use Adafruit BBIO library to blink the USR3 LED of the pocketbeagle at 5Hz

--------------------------------------------------------------------------
"""
#using code from On-Board LEDs section of README.md file at https://github.com/adafruit/adafruit-beaglebone-io-python

import Adafruit_BBIO.GPIO as GPIO
import time

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------

#End def

# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == "__main__":
    #set up LED USR3 pin for output
   for i in range(4):
        GPIO.setup("USR3", GPIO.OUT)
    #switch between between high(on) and low(off) every 0.1 sec
while True:
        for i in range(1):
            GPIO.output("USR3", GPIO.HIGH)
            time.sleep(0.1)
        for i in range(1):
            GPIO.output("USR3", GPIO.LOW)
            time.sleep(0.1) 