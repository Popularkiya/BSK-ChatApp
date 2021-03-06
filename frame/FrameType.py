from enum import Enum, auto, unique

BUFFER_SIZE = 1024


@unique
class FrameType(Enum):
    SIZE = auto()
    ACK = auto()
    MSG = auto()
    FILE = auto()
    FILE_END = auto()
    CLOSE = auto()
