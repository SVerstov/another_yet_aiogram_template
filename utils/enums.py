from enum import Enum, auto


class ChatType(Enum):
    private = auto()
    channel = auto()
    group = auto()
    supergroup = auto()
