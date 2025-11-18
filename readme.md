# GRPC ROBOT

## Generate the proto files
python -m grpc_tools.protoc -Iproto_gen=proto --python_out=. --pyi_out=. --grpc_python_out=. proto/control.proto 

# Docker

`docker run --device /dev/gpiomem -p 50051:50051 <tag>`
