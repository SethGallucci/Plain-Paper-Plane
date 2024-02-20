from typing import Iterable

from pygame import Surface, Vector2

from src.ecs.ecs import Component
from src.geometry.polygon import Polygon


class Transform(Component):
    """
    A mixin class for adding positional and rotational data to Entity-Type classes.
    :param position: The coordinates of the entity in the world.
    :param rotation: The angular orientation of the entity in the world.
    """

    def __init__(self, *, position: Vector2, rotation: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.position: Vector2 = position
        self.rotation: float = rotation


class Velocity(Transform):
    def __init__(self, *, linear_velocity: Vector2 = Vector2(0, 0), angular_velocity: float = 0, **kwargs):
        """
        A mixin class for adding motion to Entity classes.

        *Note:* This class also adds the Transform mixin via inheritance, as this class is purely an extension of Transform.
        :param linear_velocity:
        :param angular_velocity:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.linear_velocity: Vector2 = linear_velocity
        self.angular_velocity: float = angular_velocity


class PolygonCollider(Transform):
    def __init__(self, *, polygons: Iterable[Polygon], **kwargs):
        """
        A Mixin class for adding collision detection regions by way of Polygons.

        :param polygons: An iterable of Polygons. *Note:* Each Polygon must be a convex polygon whose vertices are measured from the anchor point of the Entity.
        """
        super().__init__(**kwargs)
        self.polygons: set[Polygon] = set(polygons)


class Texture(Component):
    def __init__(self, *, surface: Surface, anchor: Vector2 = Vector2(0, 0), render_height=0, **kwargs):
        """
        A mixin class for adding visual representation to Entity-Type classes.
        :param surface: A Surface used to visually represent this Entity.
        :param anchor: The Vector2 location, relative to the center of the Surface, used as the point of rotation.
        :param kwargs: Used by Component Type mixin classes for multiple inheritance.
        """
        super().__init__(**kwargs)
        self.surface: Surface = surface
        self.anchor: Vector2 = anchor
        self.render_height: int = render_height


class TileWrapTexture(Texture):
    def __init__(self, *, subsurface_size: tuple[int, int], is_horizontally_wrapped: bool = False, is_vertically_wrapped: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.subsurface_size: tuple[int, int] = subsurface_size
        self.base_image_size: tuple[int, int] = self.surface.get_size()

        tile_width: int
        tile_height: int
        tile_width, tile_height = self.base_image_size

        subsurface_width: int
        subsurface_height: int
        subsurface_width, subsurface_height = subsurface_size

        number_of_horizontal_tiles: int = subsurface_width // tile_width + (2 if is_horizontally_wrapped else 1)
        number_of_vertical_tiles: int = subsurface_height // tile_height + (2 if is_vertically_wrapped else 1)

        self.expanded_surface: Surface = Surface(
            (
                tile_width * number_of_horizontal_tiles,
                tile_height * number_of_vertical_tiles
            )
        )
        self.expanded_surface.blits(
            [
                (self.surface, (x * tile_width, y * tile_height))
                for y in range(number_of_horizontal_tiles)
                for x in range(number_of_vertical_tiles)
            ]
        )

        self.surface = self.expanded_surface.subsurface(0, 0, *subsurface_size)
