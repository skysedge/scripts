#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import sys
import termios
import atexit
from select import select


#Assign pin names numbered according to the physical pin numbers (in paranetheses when running $pinout)
x_en = 36
x_dir = 38
x_pulse = 40

y_en = 29
y_dir = 31
y_pulse = 33

th_en = 11
th_dir = 13
th_pulse = 15

GPIO.setmode(GPIO.BOARD)    #this means that pin assignments will go by the silk numbering on the TOP of the Jetson NANO

#Congifure the pins
GPIO.setup(x_en, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(x_dir, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(x_pulse, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(y_en, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(y_dir, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(y_pulse, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(th_en, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(th_dir, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(th_pulse, GPIO.OUT, initial=GPIO.LOW)


class KBHit:

    def __init__(self):
        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)


    def set_normal_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        s = ''
        return sys.stdin.read(1)

    def kbhit(self):  # Returns True if keyboard character was hit, False otherwise.
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr != []

def main():
    kb = KBHit()    #Instantiate KBHit class
        
    #Initialize velocities
    v_x = 0
    v_y = 0
    v_th = 0

    vinc = 100  #Set the step size for incrementing/decrementing the velocity
    thvinc = 5  #...for the theta axis
    dirFlag = True   #A flag to keep track of whether the velocity was most recently positive (true) or negative (false)
    enFlag = False  #A fkag to keep track of whether each drive was most recently enabled (true)

    char = 'g'  #Instantiate char as a dummy character that doesn't appear in if-else tree below
    while True:
        if kb.kbhit():
            char = kb.getch()
            print(char)

        if (char == 'q'):
            GPIO.cleanup() # cleanup the GPIO settings before exiting 
            exit(0)
        elif (char == 's'): # Zero velocity for all axes
            v_x = 0
            v_y = 0
            v_th = 0
            char = 'g'
        elif (char == 'd'): #Increase X velocity
            v_x = v_x + vinc
            char = 'g'
        elif (char == 'a'): #Decrease X velocity
            v_x = v_x - vinc
            char = 'g'
        elif (char == 'w'): 
            v_y = v_y + vinc
            char = 'g'
        elif (char == 'x'): 
            v_y = v_y - vinc
            char = 'g'
        elif (char == 'k'): 
            v_th = v_th + thvinc
            char = 'g'
        elif (char == 'j'): 
            v_th = v_th - thvinc
            char = 'g'

        ##Handle the x-axis control (should make a class for this instead)
        if (v_x > 0):       #If the x velocity is positive...
            GPIO.output(x_dir, GPIO.HIGH)   #Direction is POSITVE
        elif (v_x < 0):     #If the x velocity is negative...
            GPIO.output(x_dir, GPIO.LOW)
        if (v_x == 0):    #If x velocity is 0...
            if (enFlag) == False:
                pass 
            else:
                GPIO.output(x_en, GPIO.HIGH)     #DISABLE
                GPIO.output(x_pulse, GPIO.LOW)   #Ensure STEP/PULSE pin is low
                GPIO.output(x_dir, GPIO.LOW)    #Ensure Direction pin is low
                enFlag = False
        if (v_x != 0):      #If and only if theres nonzero velocity, send pulses...
            if (enFlag) == True:
                pass 
            else:
                GPIO.output(x_en, GPIO.LOW)    #ENABLE
                enFlag = True
            GPIO.output(x_pulse, GPIO.HIGH)  #Pulse ON
            time.sleep(1/abs(v_x))               #Delay inversely with the velocity to set pulse/motor speed
            GPIO.output(x_pulse, GPIO.LOW)   #Pulse OFF
            time.sleep(1/abs(v_x))               #Delay again. The driver prefers 50% duty.
            print(v_x)

        ##Handle the y-axis control
        if (v_y > 0):       
            GPIO.output(y_dir, GPIO.HIGH)   
        elif (v_y < 0):     
            GPIO.output(y_dir, GPIO.LOW)    
        if (v_y == 0):    
            if (enFlag) == False:
                pass 
            else:
                GPIO.output(y_en, GPIO.HIGH)     
                GPIO.output(y_pulse, GPIO.LOW)  
                GPIO.output(y_dir, GPIO.LOW)   
                enFlag = False
        if (v_y != 0):      
            if (enFlag) == True:
                pass 
            else:
                GPIO.output(y_en, GPIO.LOW)    
                enFlag = True
            GPIO.output(y_pulse, GPIO.HIGH)  
            time.sleep(1/abs(v_y))          
            GPIO.output(y_pulse, GPIO.LOW) 
            time.sleep(1/abs(v_y))        
            print(v_y)

        ##Handle the th-axis control
        if (v_th > 0):       
            GPIO.output(th_dir, GPIO.HIGH)   
        elif (v_th < 0):     
            GPIO.output(th_dir, GPIO.LOW)    
        if (v_th == 0):    
            if (enFlag) == False:
                pass 
            else:
                GPIO.output(th_en, GPIO.HIGH)     
                GPIO.output(th_pulse, GPIO.LOW)  
                GPIO.output(th_dir, GPIO.LOW)   
                enFlag = False
        if (v_th != 0):      
            if (enFlag) == True:
                pass 
            else:
                GPIO.output(th_en, GPIO.LOW)    
                enFlag = True
            GPIO.output(th_pulse, GPIO.HIGH)  
            time.sleep(1/abs(v_th))          
            GPIO.output(th_pulse, GPIO.LOW) 
            time.sleep(1/abs(v_th))        
            print(v_th)


    kb.set_normal_term()

if __name__ == "__main__":  #Run the main loop automatically iff we run this .py file directly.
    main()
