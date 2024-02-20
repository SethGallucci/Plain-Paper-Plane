from __future__ import annotations

from typing import Callable, Iterable

from src.ecs.ecs import Entity


class World:
    """
    And object used to keeping track of a collection of unique Entities.
    """
    def __init__(self, *entities: Entity):
        self._entities: dict[int, Entity] = {}
        self.add(*entities)

    def add(self, *entities: Entity) -> None:
        """
        Store references to the supplied Entities in the World.

        :param entities:
        :return:
        """
        for entity in entities:
            self._entities[entity.id] = entity

    def remove(self, *entities: Entity) -> None:
        """
        Remove references to the supplied Entities from the World.

        :param entities:
        :return:
        """
        for entity in entities:
            del self._entities[entity.id]

    def get(self, *entity_ids:int) -> tuple[Entity, ...]:
        """
        Return a
        :param entity_ids:
        :return:
        """
        return tuple(self._entities[entity_id] for entity_id in entity_ids)

    def query(self, predicate: Callable[[Entity], bool] | None = None) -> Iterable[Entity]:
        """
        Return an Iterable of Entities from the World that satisfy the supplied predicate. If called with no predicate (`None`), all the World's Entities will be supplied by the Iterable.

        :param predicate:
        :return:
        """
        return filter(predicate, self._entities.values())
