from message_queue_events.base import MessageQueueEvent

__all__ = ('RevisionEvent',)


class RevisionEvent(MessageQueueEvent):

    def __init__(self, unit_id: int, unit_name: str, revision):
        self.__unit_id = unit_id
        self.__unit_name = unit_name
        self.__revision = revision

    def get_data(self):
        return {
            'unit_id': self.__unit_id,
            'type': 'LOSSES_AND_EXCESSES',
            'payload': {
                'unit_name': self.__unit_name,
                'summary': self.__revision.dict(),
            },
        }
