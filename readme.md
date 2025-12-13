# GRPC ROBOT

## Generate the proto files
`uv run -- python -m grpc_tools.protoc -Iproto_gen=proto --python_out=. --pyi_out=. --grpc_python_out=. proto/control.proto`

## Lint 

`uv run -- ruff check .`

## Build

`uv build .`

## Run

`uv run -- python -m app.server`

`uv run -- python -m app.client`

## Docker

`docker run --device /dev/gpiomem -p 50051:50051 <tag>`
