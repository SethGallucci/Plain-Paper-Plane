from abc import ABC, abstractmethod

from pygame.event import Event


class EventHandler(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        assert len(kwargs) <= 0, "Only explicitly specified key word arguments should be passed."
        super().__init__()

    @abstractmethod
    def __call__(self, event: Event):
        pass
