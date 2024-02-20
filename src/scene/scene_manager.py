# The scene_manager is witten as a module, as it is intended to be a singleton, and this is supposedly the most
# pythonic, straightforward way to accomplish this.

from __future__ import annotations

import sys
from typing import List

from pygame import Surface, SurfaceType
from pygame.event import Event

from src.scene.scene import Scene

_this = sys.modules[__name__]

current_scene: Scene | None = None


def render(screen: Surface | SurfaceType) -> None:
    _this.current_scene.render(screen)


def process_events(events: List[Event]) -> None:
    _this.current_scene.process_events(events)


def step() -> None:
    _this.current_scene.step()


def set_scene(scene: Scene | None) -> None:
    _this.current_scene = scene
