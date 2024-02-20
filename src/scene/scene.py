from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from pygame import Surface, SurfaceType
from pygame.event import Event


class Scene(ABC):
    """
    A self-contained insert used to represent a functionally distinct and segregated segment of the game.
    :param init_data: Optional data that will be passed into the scene.
    """

    def __init__(self, init_data: dict | None = None):
        self.next_scene: Scene | None = self
        self.init_data = init_data

    @abstractmethod
    def process_events(self, events: List[Event]) -> None:
        """
        Process the events generated during this Scene.
        :param events: A list of unprocessed Events.
        """
        ...

    @abstractmethod
    def step(self) -> None:
        """
        Update the state of this Scene.
        """
        ...

    @abstractmethod
    def render(self, screen: Surface | SurfaceType) -> None:
        """
        Render to the `screen` the visuals for the Scene.
        """
        ...

    def set_next_scene(self, next_scene: Scene | None) -> None:
        """
        Set the `next_scene` variable for the scene_manager to use to transition into that Scene, or to begin termination of the program if None is passed.
        :param next_scene: The Scene into which the game will transition.
        """
        self.next_scene = next_scene
