"""
An object-based protocol means messages, commands, and events are
sent between client and server through serialized objects (like JSON).
The client sends commands and messages to the server. In response, the
server sends an event to the client when a command is executed and broadcasts
messages sent from the client to other clients in the same channel.
"""
from dataclasses import dataclass, asdict
from json import dumps, loads

@dataclass
class Command:
    cmd: str
    args: list = None


@dataclass
class Event:
    type: str
    notif: str
    optional: str = None


@dataclass
class Message:
    content: str
    sender: str = None
    channel: str = None


# Converts dataclass instance to json, referenced ai
def serialize(obj):
    return dumps(asdict(obj))


# Converts json back to one of the dataclasses
def deserialize(json_obj):
    data = loads(json_obj)

    if "cmd" in data:
        return Command(**data)
  
    elif "type" in data:
        return Event(**data)
  
    elif "content" in data:
        return Message(**data)
  
    else:
        raise ValueError("Unknown object type sent.")