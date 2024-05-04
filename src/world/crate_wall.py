import random

from pygame import SRCALPHA, Surface, Vector2
from pygame.image import load

from src.ecs.ecs import Entity
from src.geometry.polygon import Polygon
from src.world.component import PolygonCollider, Texture


class CrateWall(Entity, Texture, PolygonCollider):

    def __init__(
        self,
        *,
        position: float,
        render_height: int = 0,
        **kwargs
    ):
        crate = load("res/crate.png")
        metal_frame = load("res/metal_frame.png")
        wall = Surface((crate.get_width(), crate.get_height() * 7), flags=SRCALPHA)
        wall.fill((0, 0, 0, 0))

        crate_height = crate.get_height()
        metal_frame_location = random.randint(1, 5)
        blit_surfaces = [crate if n != metal_frame_location else metal_frame for n in range(7)]
        blit_locations = [(0, crate_height * n) for n in range(7)]
        crate_blits = list(zip(blit_surfaces, blit_locations))
        wall.blits(crate_blits)

        crate_width_half: float = crate.get_width() / 2
        wall_height_half: float = wall.get_height() / 2

        polygon_top = Polygon(
            Vector2(-crate_width_half, -wall_height_half),
            Vector2(-crate_width_half, -wall_height_half + crate_height * metal_frame_location),
            Vector2(crate_width_half, -wall_height_half + crate_height * metal_frame_location),
            Vector2(crate_width_half, -wall_height_half)
        )

        polygon_bottom = Polygon(
            Vector2(-crate_width_half, -wall_height_half + crate_height * (metal_frame_location + 1)),
            Vector2(-crate_width_half, wall_height_half),
            Vector2(crate_width_half, wall_height_half),
            Vector2(crate_width_half, -wall_height_half + crate_height * (metal_frame_location + 1))
        )

        self.metal_frame_location = metal_frame_location

        super().__init__(
            surface=wall,
            anchor=Vector2(0, 0),
            position=Vector2(position, 0),
            render_height=render_height,
            rotation=0,
            polygons=[polygon_top, polygon_bottom],
            **kwargs
        )
