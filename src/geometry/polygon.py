from __future__ import annotations

from typing import Generator

from pygame import Vector2


class Polygon:
    def __init__(self, *vertices: Vector2):
        self.vertices: tuple[Vector2, ...] = vertices

    def __add__(self, other: Vector2) -> Polygon:
        return Polygon(*(vertex + other for vertex in self.vertices))

    def __sub__(self, other):
        return self.__add__(-other)

    def rotate(self, degrees: float) -> Polygon:
        """
        Return a new polygon where each vertex is rotated around the implicit origin by the specified number of degrees.
        :param degrees:
        :return:
        """
        return Polygon(*(vertex.rotate(degrees) for vertex in self.vertices))

    def surface_normals(self) -> Generator[Vector2, None, None]:
        """
        Return a Generator of the non-normalized Vectors that sit perpendicular to each surface of the Polygon.
        :return:
        """
        return ((b - a).rotate(90) for a, b in zip(self.vertices, self.vertices[1:] + (self.vertices[0],)))
