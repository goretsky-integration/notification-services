import json
from abc import ABC, abstractmethod

__all__ = ('MessageQueueEvent',)


class MessageQueueEvent(ABC):

    def as_bytes(self) -> bytes:
        data = self.get_data()
        return json.dumps(data).encode('utf-8')

    @abstractmethod
    def get_data(self):
        pass
