#!/usr/bin/env python3
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
# import pygame # Were replacing this with 'inputs'
import PicoBorgRev3 as PicoBorgRev
from inputs import get_gamepad

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr  # Could get rid of this with inputs

# -----------------------------------------------------------------------------------------------------------------------
# Setup the PicoBorg Reverse
PBR = PicoBorgRev.PicoBorgRev()
PBR.Init()

if not PBR.foundChip:
    boards = PicoBorgRev.ScanForPicoBorgReverse()
    if len(boards) == 0:
        print ('No PicoBorg Reverse found, check you are attached :)')
    else:
        print('No PicoBorg Reverse at address %02X, but we did find boards:' % (PBR.i2cAddress))
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so it is correct, e.g.')
        print('PBR.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
PBR.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
# Ensure the communications failsafe has been disabled!
PBR.SetCommsFailsafe(False)
PBR.ResetEpo()
# End Setup the PicoBorg Reverse
# #-----------------------------------------------------------------------------------------------------------------------

# Settings for the joystick (inputs - https://github.com/zeth/inputs.git)
axisUpDown = 'ABS_Y'       # Joystick axis to read for up / down position
axisUpDownInverted = True  # Set this to True if up and down appear to be swapped
axisLeftRight = 'ABS_Z'    # Joystick axis to read for left / right position
axisLeftRightInverted = True  # Set this to True if left and right appear to be swapped
buttonResetEpo = 'BTN_TR2'  # Joystick button number to perform an EPO reset (Start)
buttonSlow = 'BTN_TL'  # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5  # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 'BTN_TR'  # Joystick button number for turning fast (R2)
interval = 0.00  # Time between updates in seconds, smaller responds faster but uses more processor time

# The gamepad events that this robot is listening for
eventList = ['BTN_TL', 'BTN_TR', 'BTN_TR2', 'ABS_Y', 'ABS_Z']

# Power settings - for BatteryBorg
voltageIn = 14.4  # Total battery voltage to the PicoBorg Reverse
voltageOut = 12.0  # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Turn all motors off at the start
PBR.MotorsOff()

try:
    print('Press CTRL+C to quit')
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    forwardBack = 0.0
    leftRight = 0.0

    # Loop indefinitely
    while running:
        # Get the latest events from the system
        hadEvent = False
        events = get_gamepad()

        # Handle each event individually
        for event in events:
            if event.code in eventList:
                hadEvent = True

            if hadEvent:
                # Get the event code
                eventCode = event.code
                
                # Forwards 0 to 127, backwards 129 to 255
                if eventCode == axisUpDown:
                    # Read axis positions (0 to 255)
                    forwardBack = event.state

                    if forwardBack > 130:
                        # Backwards is 130 to 255, converted to 0 to -125
                        forwardBack = (130 - forwardBack)
                    elif forwardBack < 125:
                        # Forwards is 0 to 125
                        forwardBack = (125 - forwardBack)
                    else:
                        # Stop is 0
                        forwardBack = 0

                    forwardBack = forwardBack / 125.0
                        
                    if axisUpDownInverted:
                        forwardBack = -forwardBack

                # Left/right
                if eventCode == axisLeftRight:
                    leftRight = event.state
                    if leftRight > 130:
                        leftRight = (130 - leftRight)
                    elif leftRight < 125:
                        leftRight = (125 - leftRight)
                    else:
                        leftRight = 0

                    leftRight = leftRight / 125.0

                    if axisLeftRightInverted:
                        leftRight = -leftRight

                # Apply steering speeds
                if eventCode == buttonFastTurn:
                    print("FastTurn")
                    leftRight *= 0.5

                # Determine the drive power levels
                driveLeft = -forwardBack
                driveRight = -forwardBack
                if leftRight < -0.05:
                    # Turning left
                    driveLeft *= 1.0 + (2.0 * leftRight)
                elif leftRight > 0.05:
                    # Turning right
                    driveRight *= 1.0 - (2.0 * leftRight)

                # Check for button presses
                if eventCode == buttonResetEpo:
                    PBR.ResetEpo()

                if eventCode == buttonSlow:
                    print("Slow")
                    driveLeft *= slowFactor
                    driveRight *= slowFactor

                # Set the motors to the new speeds
                PBR.SetMotor1(driveRight * maxPower)
                PBR.SetMotor2(-driveLeft * maxPower)

        # Change the LED to reflect the status of the EPO latch
        PBR.SetLed(PBR.GetEpo())
        # Wait for the interval period
        time.sleep(interval)

    # Disable all drives
    PBR.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    PBR.MotorsOff()
