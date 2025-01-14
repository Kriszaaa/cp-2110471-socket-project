from typing import Any

from .serializer import serialize, deserialize
from .user import User
import dataclasses


class MessageProtocolResponse:
    OK = 200
    WARN = 400
    NOT_EXIST = 404
    ERROR = 500
    EXISTS = 501


class MessageProtocolCode:
    class INSTRUCTION:
        IDENTIFY_MASTER = 1000
        IDENTIFY_SLAVES = 1001
        JOIN_SLAVE = 1002
        RESPONSE = 1003

        class BROADCAST:
            CLIENT_DISC = 1004
            SERVER_DISC = 1005

        class CLIENT:
            LIST = 2000
            RENAME = 2001

        class GROUP:
            LIST_GROUPS = 3000
            LIST_CLIENTS = 3001
            JOIN = 3002
            LEAVE = 3003
            LEAVE_ALL = 3004
            CREATE = 3005

    class DATA:
        NULL = 100
        PLAIN_TEXT = 101
        PYTHON_OBJECT = 102
        IMAGE = 103
        VIDEO = 104
        VOICE = 105
        FILE = 106

    class Data(DATA):
        pass

    @staticmethod
    def is_instruction(code) -> bool:
        return code >= 1000

    @staticmethod
    def is_data(code) -> bool:
        return not MessageProtocolCode.is_instruction(code)


class MessageProtocolFlag:
    ANNOUNCE = 10001


@dataclasses.dataclass(init=True, repr=True, order=True)
class MessageProtocol:
    src: User | None
    dst: User | None
    message_type: MessageProtocolCode
    message_flag: MessageProtocolFlag | None
    response: MessageProtocolResponse | None
    _body: bytes

    @property
    def body(self):
        return deserialize(self._body)

    @body.setter
    def body(self, v):
        self._body = serialize(v)


@dataclasses.dataclass(init=True, repr=False, order=True, frozen=True)
class FileProtocol:
    filename: str
    _size: int
    content: bytes

    @property
    def size(self):
        return len(self.content)


def new_message_proto(src: User | None,
                      dst: User | None,
                      message_type: MessageProtocolCode,
                      body: Any,
                      response: MessageProtocolResponse | None = None,
                      flag: MessageProtocolFlag | None = None):
    return MessageProtocol(
        src=src,
        dst=dst,
        message_type=message_type,
        message_flag=flag,
        response=response,
        _body=serialize(body)
    )


def new_file_proto(filename: str,
                   content: bytes):
    return FileProtocol(
        filename=filename,
        content=content,
        _size=len(content)
    )
