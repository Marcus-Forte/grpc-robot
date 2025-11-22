import grpc
import logging
import sys
import tty
import termios

# Import generated stubs (after running protoc on control.proto)
from proto_gen import control_pb2_grpc
from proto_gen import control_pb2

# Set up basic logging
logging.basicConfig(level=logging.INFO)

SERVER_ADDRESS = '192.168.3.251:50051'

def key_input_generator():
    """
    A generator that continuously yields KeyInput messages based on user input.
    The stream finishes when the user types 'exit'.
    """
    
    print("\n--- Start Typing to Stream (press 'q' to finish stream) ---")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # Set terminal to raw mode so we get single key presses
        tty.setraw(fd)
        # Ensure echo is disabled so typed characters are not shown by the terminal
        new_settings = termios.tcgetattr(fd)
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        while True:
            try:
                ch = sys.stdin.read(1)
            except (KeyboardInterrupt, EOFError):
                print("\nClient finished sending stream.")
                break

            # If user pressed 'q', exit the stream
            if ch == 'q':
                print("\nClient finished sending stream.")
                break

            # For readability, show the pressed key (non-printables shown as repr)
            display = ch if ch.isprintable() else repr(ch)
            # Clear the entire current line (ESC[2K) and print a single status line
            sys.stdout.write('\r\x1b[2K')
            sys.stdout.write(f"Sent: {display}\n")
            sys.stdout.flush()

            # If user pressed Ctrl-C or Ctrl-D, stop (representations '\x03' and '\x04')
            if ch in ('\x03', '\x04'):
                print("\nClient finished sending stream.")
                break

            # Yield the KeyInput message using the generated stub
            yield control_pb2.KeyInput(key_value=ch)

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def run():
    """
    Connects to the gRPC server and initiates the client stream.
    """
    try:
        # Connect to the server
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            # Get the stub from the generated gRPC file
            stub = control_pb2_grpc.KeyboardServiceStub(channel)
            
            logging.info(f"Connecting to server at {SERVER_ADDRESS}")
            
            # Initiate the client streaming RPC with the generator
            # We don't need to capture the Empty response explicitly
            stub.SendKeyboardStream(key_input_generator())
            
            logging.info("Stream RPC complete. Server acknowledged receipt.")
            
    except grpc.RpcError as e:
        logging.error(f"RPC failed: {e.code()} - {e.details()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    run()