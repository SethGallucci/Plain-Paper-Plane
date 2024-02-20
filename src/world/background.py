from pygame import Surface, Vector2
from pygame.image import load

from src.ecs.ecs import Entity
from src.world.component import TileWrapTexture, Transform


class Background(Entity, TileWrapTexture, Transform):
    def __init__(
        self,
        *,
        position: Vector2 = Vector2(0, 0),
        render_height: int = 0,
        **kwargs
    ):
        image: Surface = load("res/game_background.png").convert_alpha()
        super().__init__(
            surface=image,
            subsurface_size=image.get_size(),
            anchor=Vector2(image.get_size()) * -0.5,
            position=position,
            render_height=render_height,
            rotation=0,
            **kwargs
        )
