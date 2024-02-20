from __future__ import annotations

from pygame import Surface, Vector2

from src.ecs.ecs import Entity
from src.world.component import Texture, Transform


class Camera(Entity, Texture, Transform):
    def __init__(
        self,
        *,
        surface: Surface,
        anchor: Vector2 = Vector2(0, 0),
        position: Vector2 = Vector2(0, 0)
    ):
        super().__init__(
            surface=surface,
            anchor=anchor,
            position=position,
            rotation=0
        )
