from __future__ import annotations

from typing import Iterable

from pygame import Color, Rect, Surface, Vector2
from pygame.draw import polygon as draw_polygon
from pygame.transform import rotate

from src.ecs.ecs import Entity, System
from src.geometry.polygon import Polygon
from src.world.camera import Camera
from src.world.component import PolygonCollider, Texture, TileWrapTexture, Transform, Velocity


class Render(System):
    """
    A System that renders the supplied Iterable of Entities to a specified Camera.
    To be rendered, an Entitiy must have the Texture and Transform mixins.
    """

    def __init__(self, camera: Camera):
        self.camera: Camera = camera
        super().__init__(
            action=self._transform_entity_texture,
            predicate=lambda entity: isinstance(entity, Texture) and isinstance(entity, Transform) and not isinstance(entity, Camera)
        )

    def __call__(self, entities: Iterable[Entity], **kwargs) -> None:
        render_tuples = super().__call__(entities, **kwargs)
        list(render_tuples).sort(key=lambda triple: triple[0])
        render_height, surfaces, rects = zip(*render_tuples)
        blit_tuples = list(zip(surfaces, rects))
        self.camera.surface.blits(blit_tuples)

    # The Type hinting for entity should be something like Intersection[Texture, Transform],
    # but Python doesn't yet have intersections for Type hinting.
    def _transform_entity_texture(self, entity: Texture | Transform) -> (int, Surface, Rect):

        # PyGame mixes rotation handedness between modules.
        surface = rotate(entity.surface, -entity.rotation)
        return (
            entity.render_height,
            surface,
            surface.get_rect(
                center=(
                    entity.position
                    - entity.anchor.rotate(entity.rotation)
                    - self.camera.position
                    + self.camera.anchor
                )
            )
        )


class Move(System):
    """
    A System that updates the position and rotation of the supplied Iterable of Entities using the velocities (angular and linear) of each Entity.
    To be moved, an Entity must have the Velocity Mixin.
    """

    def __init__(self):
        super().__init__(
            action=self._update_entity_transform,
            predicate=lambda entity: isinstance(entity, Velocity)
        )

    @staticmethod
    def _update_entity_transform(entity: Velocity) -> None:
        entity.rotation += entity.angular_velocity
        entity.position += entity.linear_velocity


class Parallax(System):
    """
    A System which updates the subsurfaces of the supplied Iterable of TileWrapTextures as per the position of the specified Camera relative to the specified parallax_origin to produce a parallax visual effect.
    To be parallaxed, an Entity must have the TileWrapTexture mixin.
    """

    def __init__(self, camera: Camera, parallax_origin: Vector2, parallax_factor: tuple[float, float]):
        self.camera: Camera = camera
        self.parallax_origin: Vector2 = parallax_origin
        self.parallax_factor: tuple[float, float] = parallax_factor
        super().__init__(
            action=self._position_subsurface,
            predicate=lambda entity: isinstance(entity, TileWrapTexture)
        )

    def _position_subsurface(self, entity: TileWrapTexture) -> None:
        parallax_factor_horizontal: float
        parallax_factor_vertical: float
        parallax_factor_horizontal, parallax_factor_vertical = self.parallax_factor

        base_image_size_horizontal: int
        base_image_size_vertical: int
        base_image_size_horizontal, base_image_size_vertical = entity.base_image_size

        camera_displacement: Vector2 = self.camera.position - self.parallax_origin
        parallax_shift_horizontal: float = (camera_displacement.x * parallax_factor_horizontal) % base_image_size_horizontal
        parallax_shift_vertical: float = (camera_displacement.y * parallax_factor_vertical) % base_image_size_vertical

        entity.surface = entity.expanded_surface.subsurface(parallax_shift_horizontal, parallax_shift_vertical, *entity.subsurface_size)


class VisualizePolygons(System):
    """
    A System which renders the sides of the Polygons of the supplied Iterable of Entities to the specified Camera, using the specified color and line width.
    To have its Polygons visualized, an Entity must have the PolygonCollider mixin.

    Note: This is System intended for debugging purposes.
    """

    def __init__(self, camera: Camera, color: Color = "blue", line_width: int = 3):
        self.camera: Camera = camera
        self.color: Color = color
        self.line_width: int = line_width

        super().__init__(
            action=self._draw_polygons,
            predicate=lambda entity: isinstance(entity, PolygonCollider)
        )

    def _draw_polygons(self, entity: PolygonCollider) -> None:
        for polygon in entity.polygons:
            draw_polygon(
                self.camera.surface,
                color=self.color,
                points=(polygon.rotate(entity.rotation) + (entity.position - self.camera.position + self.camera.anchor)).vertices,
                width=self.line_width
            )


class DetectCollisions(System):
    """
    A System which returns all pairs of unique Entities from the supplied Iterable of Entities that have at least one overlapping Polygon.
    The system returns each collision pair in tandem with a set of the pairs of Polygons that were overlapping between the two Entities.
    To have its Polygons checked for collisions, an Entity must have the PolygonCollider mixin.
    """

    def __init__(self):
        super().__init__(
            action=self._check_entity_collision,
            predicate=lambda entity: isinstance(entity, PolygonCollider)
        )

    def __call__(self, entities: Iterable[Entity], **kwargs) -> tuple[tuple[PolygonCollider, PolygonCollider, set], ...]:
        return tuple(filter(lambda test: len(test[2]) > 0, super().__call__(entities, **kwargs)))

    @staticmethod
    def _check_polygon_collision(polygon_0: Polygon, polygon_1: Polygon) -> bool:

        # Separating Axis Theorem
        for normal in list(polygon_0.surface_normals()) + list(polygon_1.surface_normals()):
            p0_projection = {vertex.dot(normal) for vertex in polygon_0.vertices}
            p1_projection = {vertex.dot(normal) for vertex in polygon_1.vertices}

            projection_bounds = [
                (min(p0_projection), 0),
                (max(p0_projection), 0),
                (min(p1_projection), 1),
                (max(p1_projection), 1)
            ]

            projection_bounds.sort(key=lambda x: x[0])

            if projection_bounds[0][1] == projection_bounds[1][1]:
                return False

        return True

    # The Type hinting for entity_0 and entity_1 should be something like Intersection[Entity, PolygonCollider],
    # but python doesn't yet have intersections for Type hinting.
    @classmethod
    def _check_entity_collision(cls, entity_0: PolygonCollider, entity_1: PolygonCollider) -> tuple[PolygonCollider, PolygonCollider, set]:
        collision_pairs = set()

        e0_polygon: Polygon
        for e0_polygon in entity_0.polygons:
            e0pr = e0_polygon.rotate(entity_0.rotation)

            e1_polygon: Polygon
            for e1_polygon in entity_1.polygons:
                e1pr = e1_polygon.rotate(entity_1.rotation) + entity_1.position - entity_0.position

                if cls._check_polygon_collision(e0pr, e1pr):
                    collision_pairs.add((e0_polygon, e1_polygon))

        return entity_0, entity_1, collision_pairs
