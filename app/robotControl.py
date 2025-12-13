from gpiozero import DigitalOutputDevice
import time
from enum import Enum

"""
Mfr:         back: 0b00010000 | forward: 0b00000010
Mfl:         back: 0b00000001 | forward: 0b01000000
Mbl:         back: 0b00100000 | forward: 0b10000000
Mbr:         back: 0b00001000 | forward: 0b00000100

All Forward: 0b11000110
Turn Left:   0b00100111
Turn Right:   0b11011000
All Back:   0b00111001

Stop:       0b0
"""

# --- Hardware Setup (Define the BCM GPIO pin numbers here) ---
DATA_PIN = 17    # Serial Data Input (DS) -> IDUINO PIN D8
CLOCK_PIN = 27   # Shift Register Clock (SHCP) -> IDUINO PIN D4
LATCH_PIN = 22   # Storage Register Clock / Latch (STCP) -> IDUINO PIN D12
OUTPUT_ENABLE_PIN = 23 # Output Enable (OE) -> IDUINO PIN D7 (active LOW)

# Create a small delay to ensure the register has time to react.
# A small delay is often needed, especially in non-real-time OS environments like Raspberry Pi OS.
TINY_DELAY = 0.001

# --- Initialize the GPIO pins as Output Devices ---
# OutputDevice will default to a LOW state when initialized.
data_out = DigitalOutputDevice(DATA_PIN)
clock_out = DigitalOutputDevice(CLOCK_PIN)
latch_out = DigitalOutputDevice(LATCH_PIN)
output_enable = DigitalOutputDevice(OUTPUT_ENABLE_PIN)  # OE pin, active LOW

class Direction(Enum):
    FORWARD = 0b11000110
    LEFT = 0b00100111
    RIGHT = 0b11011000
    STOP = 0b00000000
    BACKWARD = 0b00111001

class RobotControl:
    """
    RobotControl class to manage robot movements via shift register.
    """
    def activate(self, enable: bool):
        if enable:
            output_enable.off()  # Enable outputs (active LOW)
        else:
            output_enable.on()  # Disable outputs (active HIGH)

    def move(self, direction: Direction):
        """
        Moves the robot in the specified direction by shifting out the direction byte.

        Args:
            direction_byte (int): The 8-bit value representing the movement direction.
        """
        
        if not isinstance(direction, Direction):
            raise ValueError("direction must be a Direction enum value")
        
        self.__shift_out_8bit(direction.value)

    def __shift_out_8bit(self, data_byte: int):
        """
        Shifts an 8-bit integer (0-255) into a shift register.

        Args:
            data_byte (int): The 8-bit value to send (e.g., 0b10101010 or 170).
        """

        # 1. Start the Latch Sequence: Pull LATCH LOW to enable data loading
        latch_out.off()
        time.sleep(TINY_DELAY)

        # 2. Shift the 8 bits
        # We iterate 8 times, from the most significant bit (7) down to the least significant bit (0).
        for i in range(8):
            # 2a. Calculate the current bit's value (0 or 1)
            # We use a bitwise AND (&) with a mask that shifts left (1 << i).
            # We check the bits from 7 down to 0, which is typically the order required.
            bit = (data_byte>> (7 - i)) & 1

            # 2b. Set the Data pin (DS)
            if bit:
                data_out.on()
            else:
                data_out.off()

            time.sleep(TINY_DELAY)

            # 2c. Toggle the Clock pin (SHCP) to load the bit
            clock_out.on()
            time.sleep(TINY_DELAY)
            clock_out.off()
            time.sleep(TINY_DELAY)

        # 3. End the Latch Sequence: Pull LATCH HIGH to update the outputs
        latch_out.on()
        time.sleep(TINY_DELAY)

        print(f"Shifted out byte: {data_byte:08b}")