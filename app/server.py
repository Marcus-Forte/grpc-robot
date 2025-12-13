import grpc
import time
from concurrent import futures
from queue import Queue
from queue import Empty as EmptyQueue
import threading
import logging

from .robotControl import RobotControl, Direction
# Import generated stubs (requires running the protoc command first)
from proto_gen import control_pb2_grpc, control_pb2
from google.protobuf.empty_pb2 import Empty

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def process_commands(command_queue: Queue, stop_event: threading.Event):
        """Process queued Move commands on a dedicated thread."""
        while not stop_event.is_set():
            try:
                cmd = command_queue.get(timeout=0.5)
            except EmptyQueue:
                continue

            direction = cmd.get("direction")
            duration = cmd.get("duration", 0)

            move_map = {
                control_pb2.MoveDirection.MOVE_FORWARD: Direction.FORWARD,
                control_pb2.MoveDirection.MOVE_LEFT: Direction.LEFT,
                control_pb2.MoveDirection.MOVE_RIGHT: Direction.RIGHT,
                control_pb2.MoveDirection.MOVE_BACKWARD: Direction.BACKWARD,
            }

            target_direction = move_map.get(direction)
            if target_direction is None:
                logging.warning(f"Invalid direction received: {direction}")
                command_queue.task_done()
                continue

            robot.activate(True)
            robot.move(target_direction)
            time.sleep(duration)
            robot.move(Direction.STOP)
            robot.activate(False)

            command_queue.task_done()

# Define the Servicer class that implements the RPC methods
class RobotControlServicer(control_pb2_grpc.RobotControlServicer):
    """
    Implements the RobotControl methods defined in the .proto file.
    """
    def __init__(self, robot: RobotControl, command_queue: Queue):
        self.robot = robot
        self.command_queue = command_queue

    def SendKeyboardStream(self, request_iterator, context):
        """
        Implements the client-streaming RPC.
        The client sends a stream of KeyInput messages.
        The server processes them and returns a single StreamSummary.
        """
        logging.info("--- New Client Stream Started ---")
        key_count = 0
        self.robot.activate(True)
        
        # Iterate over the stream of messages sent by the client
        for key_input in request_iterator:
            key_count += 1
            logging.info(f"Received Key #{key_count}: '{key_input.key_value}' ")
            # In a real application, you would process this key input here
            
            # Optional: Add a small delay to simulate processing time
            # time.sleep(0.01) 
            if(key_input.key_value == "w"):
                print("onwards")
                self.robot.move(Direction.FORWARD)
            elif(key_input.key_value == "a"):
                print("left")
                self.robot.move(Direction.LEFT)
            elif(key_input.key_value == "d"):
                print("right")
                self.robot.move(Direction.RIGHT)
            elif(key_input.key_value == "s"):
                print("stop")
                self.robot.move(Direction.STOP)
            elif(key_input.key_value == "x"):
                print("back")
                self.robot.move(Direction.BACKWARD)


        logging.info(f"--- Client Stream Finished. Total keys received: {key_count} ---")
        
        # After the client has finished streaming, return the single response
        self.robot.move(Direction.STOP)
        self.robot.activate(False)

        return Empty()
    
    def Move(self, request, context):
        """
        Implements the unary RPC for Move.
        The client sends a MoveRequest and receives an empty response.
        """
        logging.info(f"Received Move command: direction={request.direction}, duration={request.duration}")

        self.command_queue.put(
            {
                "direction": request.direction,
                "duration": request.duration,
            }
        )

        return Empty()

def serve(robot: RobotControl):
    
    """
    Sets up and runs the gRPC server.
    """
    command_queue: Queue = Queue()
    stop_event = threading.Event()

    # Create a gRPC server with a thread pool for handling requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    
    # Add the implemented service servicer to the server
    control_pb2_grpc.add_RobotControlServicer_to_server(
        RobotControlServicer(robot, command_queue), server
    )
    
    
    # Define the address and port
    server_address = '[::]:50051'
    server.add_insecure_port(server_address)
    
    # Start the server
    server.start()
    logging.info(f"Server started, listening on {server_address}")

    worker = threading.Thread(target=process_commands(command_queue, stop_event), daemon=True)
    worker.start()
    
    # Keep the main thread running until the server is stopped
    try:
        while True:
            time.sleep(86400) # One day
    except KeyboardInterrupt:
        stop_event.set()
        server.stop(0)
        logging.info("Server stopped gracefully.")

if __name__ == '__main__':
    robot = RobotControl()

    serve(robot)