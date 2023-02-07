from typing import TypeVar, Iterable, Callable, TypeAlias

__all__ = ('filter_by_predicates', 'filter_via_any_predicate')

T = TypeVar('T')

Predicate: TypeAlias = Callable[..., bool]


# TODO rename to 'filter_via_all_predicates'
def filter_by_predicates(elements: Iterable[T], *predicates: Predicate) -> list[T]:
    return [element for element in elements
            if all((predicate(element) for predicate in predicates))]


def filter_via_any_predicate(elements: Iterable[T], *predicates: Predicate) -> list[T]:
    return [element for element in elements
            if any((predicate(element) for predicate in predicates))]
