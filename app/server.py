import grpc
import time
from concurrent import futures
import logging

from .robotControl import RobotControl, Direction
# Import generated stubs (requires running the protoc command first)
from proto_gen import control_pb2_grpc, control_pb2
from google.protobuf.empty_pb2 import Empty

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Define the Servicer class that implements the RPC methods
class RobotControlServicer(control_pb2_grpc.RobotControlServicer):
    """
    Implements the RobotControl methods defined in the .proto file.
    """
    def __init__(self, robot: RobotControl):
        self.robot = robot

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

        self.robot.activate(True)

        if(request.direction == control_pb2.MoveDirection.MOVE_FORWARD):
            self.robot.move(Direction.FORWARD)
        elif(request.direction == control_pb2.MoveDirection.MOVE_LEFT):
            self.robot.move(Direction.LEFT)
        elif(request.direction == control_pb2.MoveDirection.MOVE_RIGHT):
            self.robot.move(Direction.RIGHT)
        elif(request.direction == control_pb2.MoveDirection.MOVE_DOWN):
            self.robot.move(Direction.BACKWARD)
        else:
            print("Invalid direction, stopping.")

        time.sleep(request.duration)
        self.robot.move(Direction.STOP)
        self.robot.activate(False)
        
        return Empty()

def serve(robot: RobotControl):
    
    """
    Sets up and runs the gRPC server.
    """
    # Create a gRPC server with a thread pool for handling requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    
    # Add the implemented service servicer to the server
    control_pb2_grpc.add_RobotControlServicer_to_server(
        RobotControlServicer(robot), server
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
    robot = RobotControl()

    serve(robot)