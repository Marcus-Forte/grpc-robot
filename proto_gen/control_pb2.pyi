from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KeyInput(_message.Message):
    __slots__ = ("key_value",)
    KEY_VALUE_FIELD_NUMBER: _ClassVar[int]
    key_value: str
    def __init__(self, key_value: _Optional[str] = ...) -> None: ...
