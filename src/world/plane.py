from pygame import Vector2
from pygame.image import load

from src.ecs.ecs import Entity
from src.geometry.polygon import Polygon
from src.world.component import PolygonCollider, Texture, Velocity


class Plane(Entity, Texture, Velocity, PolygonCollider):
    def __init__(
        self,
        *,
        position: Vector2 = Vector2(0, 0),
        rotation: float = 0,
        render_height: int = 0,
        linear_velocity: Vector2 = Vector2(0, 0),
        angular_velocity: float = 0,
        **kwargs
    ):
        super().__init__(
            surface=load("res/plane.png"),
            anchor=Vector2(0, 0),
            render_height=render_height,
            position=position,
            rotation=rotation,
            linear_velocity=linear_velocity,
            angular_velocity=angular_velocity,
            polygons=[Polygon(Vector2(30, 0), Vector2(-26, -6), Vector2(-30, 6))],
            **kwargs
        )
