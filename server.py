from gpiozero import DigitalOutputDevice
import sys
import grpc
import time
from concurrent import futures
import logging

# Import generated stubs (requires running the protoc command first)
from proto_gen import control_pb2_grpc
from google.protobuf.empty_pb2 import Empty

# Set up basic logging
logging.basicConfig(level=logging.INFO)
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
# NOTE: Replace the numbers below with the actual GPIO BCM pin numbers
# you have connected to your shift register's pins.
DATA_PIN = 17    # Serial Data Input (DS) -> IDUINO PIN D8
CLOCK_PIN = 27   # Shift Register Clock (SHCP) -> IDUINO PIN D4
LATCH_PIN = 22   # Storage Register Clock / Latch (STCP) -> IDUINO PIN D12
OUTPUT_ENABLE_PIN = 23 # Output Enable (OE) -> IDUINO PIN D7 (active LOW)

# --- Initialize the GPIO pins as Output Devices ---
# OutputDevice will default to a LOW state when initialized.
data_out = DigitalOutputDevice(DATA_PIN)
clock_out = DigitalOutputDevice(CLOCK_PIN)
latch_out = DigitalOutputDevice(LATCH_PIN)
output_enable = DigitalOutputDevice(OUTPUT_ENABLE_PIN)  # OE pin, active LOW

# Create a small delay to ensure the register has time to react.
# A small delay is often needed, especially in non-real-time OS environments like Raspberry Pi OS.
TINY_DELAY = 0.001

def shift_out_8bit(data_byte):
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
        bit = (data_byte >> (7 - i)) & 1

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


# Define the Servicer class that implements the RPC methods
class KeyboardServiceServicer(control_pb2_grpc.KeyboardServiceServicer):
    """
    Implements the KeyboardService methods defined in the .proto file.
    """

    def SendKeyboardStream(self, request_iterator, context):
        """
        Implements the client-streaming RPC.
        The client sends a stream of KeyInput messages.
        The server processes them and returns a single StreamSummary.
        """
        logging.info("--- New Client Stream Started ---")
        key_count = 0
        output_enable.off()  # Enable outputs (active LOW)
        
        # Iterate over the stream of messages sent by the client
        for key_input in request_iterator:
            key_count += 1
            logging.info(f"Received Key #{key_count}: '{key_input.key_value}' ")
            # In a real application, you would process this key input here
            
            # Optional: Add a small delay to simulate processing time
            # time.sleep(0.01) 
            if(key_input.key_value == "w"):
                print("onwards")
                shift_out_8bit(0b11000110)
            elif(key_input.key_value == "a"):
                print("left")
                shift_out_8bit(0b00100111)
            elif(key_input.key_value == "d"):
                print("right")
                shift_out_8bit(0b11011000)
            elif(key_input.key_value == "s"):
                print("stop")
                shift_out_8bit(0)
            elif(key_input.key_value == "x"):
                print("back")
                shift_out_8bit(0b00111001)


        logging.info(f"--- Client Stream Finished. Total keys received: {key_count} ---")

        # After the client has finished streaming, return the single response
        shift_out_8bit(0)
        output_enable.on()
        return Empty()

def serve():
    """
    Sets up and runs the gRPC server.
    """
    # Create a gRPC server with a thread pool for handling requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    
    # Add the implemented service servicer to the server
    control_pb2_grpc.add_KeyboardServiceServicer_to_server(
        KeyboardServiceServicer(), server
    )
    
    # Define the address and port
    server_address = '[::]:50051'
    server.add_insecure_port(server_address)
    
    # Start the server
    server.start()
    logging.info(f"Server started, listening on {server_address}")
    
    # Keep the main thread running until the server is stopped
    try:
        while True:
            time.sleep(86400) # One day
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("Server stopped gracefully.")

if __name__ == '__main__':
    shift_out_8bit(0)
    serve()