#!/usr/bin/env python3

from enum import Enum, auto
import sys
import tty
import termios
import time
import RPi.GPIO as GPIO


class Axis(Enum):
    """Let the enum describe the degrees of freedom."""
    X = auto(),
    """Forwards/Backwards"""
    Y = auto(),
    """Left/Right"""
    T = auto()  # Theta
    """Yaw"""


MOTORS = {
    Axis.X: {'ena': 36, 'dir': 38, 'pul': 40},
    Axis.Y: {'ena': 29, 'dir': 31, 'pul': 33},
    Axis.T: {'ena': 11, 'dir': 13, 'pul': 15}
}
"""Let the dictionary define the pins associated with the X, Y, and Theta axes."""


def setup_pins() -> None:
    """Configure the GPIO pins for moving stepper motor control."""

    # Identify the pins based on the silk numbering.
    GPIO.setmode(GPIO.BOARD)

    # Iterate each motor.
    for axis, pins in MOTORS.items():
        # Configure the pins associated with the motor.
        GPIO.setup(pins["ena"], GPIO.OUT, initial=GPIO.LOW)  # ENABLED
        GPIO.setup(pins["dir"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pins["pul"], GPIO.OUT, initial=GPIO.LOW)


STEP_SIZES = (1, 5, 10)
"""Let the list define each step size for the number of pulses."""
PULSE_DELAY = 0.001
"""The pulse delay is a floating point number of seconds."""


def move(axis: Axis, num_pulses: int, is_positive: bool) -> None:
    """
    Move the stage along the given axis. The velocity vector includes the number of pulses and direction of movement,
    so the boolean indicating whether velocity is positive essentially indicates the direction along the axis.

    :param axis: The axis along which to move the stage
    :param num_pulses: The numbers of pulses to generate
    :param is_positive: Indicate whether the velocity should be positive or negative
    """

    # Set the direction of movement.
    GPIO.output(MOTORS[axis]["dir"], GPIO.HIGH if is_positive else GPIO.LOW)
    time.sleep(PULSE_DELAY)

    for _ in range(num_pulses):
        # The driver prefers a 50% duty cycle.
        GPIO.output(MOTORS[axis]["pul"], GPIO.HIGH)  # Pulse ON
        time.sleep(PULSE_DELAY)
        GPIO.output(MOTORS[axis]["pul"], GPIO.LOW)  # Pulse OFF
        time.sleep(PULSE_DELAY)


def decrement_pulses(num_pulses: int, step_size: int) -> int:
    """
    Decrement the number of pulses according to the step size. The minimum number of pulses is one.

    :param num_pulses: The current number of pulses
    :param step_size: The number of pulses per step
    :return: The updated number of pulses
    """

    # Update the number of pulses.
    num_pulses -= step_size
    # Check whether the number of pulses is less than the minimum.
    return num_pulses if num_pulses > 0 else 1


def increment_index(ss_idx: int) -> int:
    """
    Update the index in the list of pulse step sizes.

    :param ss_idx: The pulse step size index
    :return:  The updated pulse step size index
    """

    return (ss_idx + 1) % len(STEP_SIZES)


def read_char() -> str:
    """Read a single character from the terminal."""
    # Flush the buffer for standard input.
    termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    # Block until the users enters a character.
    return sys.stdin.read(1)


def event_loop() -> None:
    """The function implements the main event loop."""
    # Initialize the state of the state controller.
    ss_idx = 0  # Step Size Index
    tp = STEP_SIZES[ss_idx]  # Translation Pulses
    rp = STEP_SIZES[ss_idx]  # Rotation Pulses
    is_enabled = True  # Stage Control

    while True:
        # Match the character against the defined cases.
        match read_char().lower():
            case "w":  # Translate Forwards
                if is_enabled:
                    move(axis=Axis.Y, num_pulses=tp, is_positive=True)

            case "s":  # Translate Backwards
                if is_enabled:
                    move(axis=Axis.Y, num_pulses=tp, is_positive=False)

            case "a":  # Translate Left
                if is_enabled:
                    move(axis=Axis.X, num_pulses=tp, is_positive=False)

            case "d":  # Translate Right
                if is_enabled:
                    move(axis=Axis.X, num_pulses=tp, is_positive=True)

            case "e":  # Increment Translation Pulses
                print(f"Translation Pulses: {(tp := tp + STEP_SIZES[ss_idx])}")

            case "q":  # Decrement Translation Pulses
                print(f"Translation Pulses: {(tp := decrement_pulses(tp, STEP_SIZES[ss_idx]))}")

            case "r":  # Reset Step Sizes
                print(f"Translation Pulses: {(tp := STEP_SIZES[0])}")
                print(f"Rotation Pulses: {(rp := STEP_SIZES[0])}")

            case "c":  # Cycle Step Size
                print(f"Step Size: {(STEP_SIZES[ss_idx := increment_index(ss_idx)])} Pulses")

            case "j":  # Rotate Left
                if is_enabled:
                    move(axis=Axis.T, num_pulses=rp, is_positive=False)

            case "k":  # Rotate Right
                if is_enabled:
                    move(axis=Axis.T, num_pulses=rp, is_positive=True)

            case "h":  # Decrement Rotation Pulses
                print(f"Rotation Pulses: {(rp := decrement_pulses(rp, STEP_SIZES[ss_idx]))}")

            case "l":  # Increment Rotation Pulses
                print(f"Rotation Pulses: {(rp := rp + STEP_SIZES[ss_idx])}")

            case " ":  # Enable/Disable Stage Control
                print(f"Stage Control: {'Enabled' if (is_enabled := not is_enabled) else 'Disabled'}")


def main():
    # Save the current terminal settings.
    # https://docs.python.org/3/library/termios.html
    terminal_settings = termios.tcgetattr(sys.stdin.fileno())

    try:
        # Configure the GPIO pins for output.
        setup_pins()

        # Change the mode of standard input to cbreak.
        # https://docs.python.org/3/library/tty.html
        # The cbreak routine disables line buffering and erase/kill character-processing (interrupt and flow control
        # characters are unaffected), making characters typed by the user immediately available to the program.
        # https://linux.die.net/man/3/cbreak
        tty.setcbreak(sys.stdin.fileno())

        # Enter the event loop.
        event_loop()

    except KeyboardInterrupt:
        # There is no special procedure for keyboard interrupts.
        pass

    finally:
        # Mitigate the risk of damage by resetting all configured pins to input mode.
        # This only cleans up pins configured in this program.
        GPIO.cleanup()

        # Restore the terminal settings.
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, terminal_settings)


# Run the main loop automatically iff we run this .py file directly.
if __name__ == "__main__":
    main()

