from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import Parameter, signature
from itertools import combinations, permutations
from typing import Any, Callable, Iterable


class Entity(ABC):

    _next_id: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = Entity._next_id
        Entity._next_id += 1

    @property
    def id(self):
        return self._id


class Component(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class System:
    def __init__(
        self,
        # The type hinting for action should be something like Callable[[*Entity], Any],
        # but Python doesn't yet have variadic type hinting for Callable.
        action: Callable,
        is_symmetric: bool = True,
        predicate: Callable[[Entity], bool] = lambda _: True
    ):
        """
        A bundle that contains an `action` function that is applied to an Iterable of Entities when called, the specification of whether the `action` function is symmetric, and a predicate to filter out certain Entities before the `action` function is applied.
        :param action: The function that is to be applied to the supplied Entities. Note: all positional arguments (specifically `POSITIONAL_OR_KEYWORD`) should be reserved for Entity parameters. If keyword parameters are to be included, they must be segregated with a `*`. For example: `def my_action(en0, en1, en2, *, my_keyword): ...`
        :param is_symmetric: Should alternate orderings of Entities be treated as identical? In effect, should (a, b, c, d) be treated the same as (d, c, a, b)? Note: when `is_symmetric` is True, each **combination** of Entities will only ever be processed once per System call; whereas when `is_symmetric` is False, each **permutation** of Entities will be processed once per System call.
        :param predicate: A function used to filter Entities before applying the `action` function.
        """
        self._action: Callable = action
        self._action_domain_size = sum(1 for param in signature(action).parameters.values() if param.kind == Parameter.POSITIONAL_OR_KEYWORD)
        self._is_symmetric: bool = is_symmetric
        self._predicate: Callable[[Entity], bool] = predicate

    def __call__(self, entities: Iterable[Entity], **kwargs) -> tuple[Any, ...]:
        product_type = combinations if self._is_symmetric else permutations
        product = product_type(filter(self._predicate, entities), self._action_domain_size)
        return tuple(self._action(*entity_tuple, **kwargs) for entity_tuple in product)
