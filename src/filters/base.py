from typing import TypeVar, Iterable, Callable

__all__ = ('filter_by_predicates',)

T = TypeVar('T')


def filter_by_predicates(elements: Iterable[T], *predicates: Callable[..., bool]) -> list[T]:
    return [element for element in elements
            if all((predicate(element) for predicate in predicates))]
