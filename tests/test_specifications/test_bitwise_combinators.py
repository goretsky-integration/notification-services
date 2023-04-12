import pytest

from filters.specifications import (
    AndSpecification,
    FilterSpecification, OrSpecification,
)


class EqualToSpecification(FilterSpecification):

    def __init__(self, equal_to: int | float):
        self.__equal_to = equal_to

    def is_satisfied(self, item: int | float) -> bool:
        return item == self.__equal_to


class NotEqualToSpecification(FilterSpecification):

    def __init__(self, not_equal_to: int | float):
        self.__not_equal_to = not_equal_to

    def is_satisfied(self, item: int | float) -> bool:
        return item != self.__not_equal_to


class GreaterThanSpecification(FilterSpecification):

    def __init__(self, greater_than: int | float):
        self.__greater_than = greater_than

    def is_satisfied(self, item: int | float):
        return item > self.__greater_than


class LowerThanSpecification(FilterSpecification):

    def __init__(self, lower_than: int | float):
        self.__lower_than = lower_than

    def is_satisfied(self, item: int | float):
        return item < self.__lower_than


def test_bitwise_invert_specification():
    not_equal_specification = NotEqualToSpecification(10)
    equal_specification = ~not_equal_specification
    assert equal_specification.is_satisfied(10)
    assert not not_equal_specification.is_satisfied(10)


def test_bitwise_and_combine():
    between_50_and_100 = (
            GreaterThanSpecification(50)
            & LowerThanSpecification(100)
            & EqualToSpecification(55)
    )
    assert isinstance(between_50_and_100, AndSpecification)


def test_bitwise_or_combine():
    either_55_or_60 = EqualToSpecification(55) | EqualToSpecification(60)
    assert either_55_or_60.is_satisfied(55)
    assert either_55_or_60.is_satisfied(60)
    assert not either_55_or_60.is_satisfied(99)
    assert isinstance(either_55_or_60, OrSpecification)


@pytest.mark.parametrize(
    'greater_than, lower_than, value',
    [
        (66, 67, 66.5),
        (15, 17, 16),
        (5, 10, 6),
        (10, 11, 10.5),
        (1000, 10000, 5000),
    ]
)
def test_in_range(
        greater_than,
        lower_than,
        value,
):
    specification = (
            GreaterThanSpecification(greater_than)
            & LowerThanSpecification(lower_than)
    )
    assert specification.is_satisfied(value)


@pytest.mark.parametrize(
    'greater_than, lower_than, value',
    [
        (50, 100, 100),
        (50, 100, 500),
        (99, 100, 100),
        (99, 100, 99),
        (5, 10, 5),
        (5, 10, 10),
        (10, 11, 10),
        (10, 11, 11),
    ]
)
def test_not_in_range(
        greater_than,
        lower_than,
        value,
):
    specification = (
            GreaterThanSpecification(greater_than)
            & LowerThanSpecification(lower_than)
    )
    assert not specification.is_satisfied(value)


@pytest.mark.parametrize(
    'greater_than, lower_than, value',
    [
        (50, 100, 90),
        (10, 20, 15),
        (5, 10, 7),
    ]
)
def test_in_range_and_equal_to(greater_than, lower_than, value):
    specification = (
            GreaterThanSpecification(greater_than)
            & LowerThanSpecification(lower_than)
            & EqualToSpecification(value)
    )
    assert specification.is_satisfied(value)


@pytest.mark.parametrize(
    'greater_than, lower_than, value, not_equal_to',
    [
        (50, 100, 90, 91),
        (10, 20, 15, 13),
        (5, 10, 7, 8),
    ]
)
def test_in_range_and_equal_to(greater_than, lower_than, value, not_equal_to):
    specification = (
            GreaterThanSpecification(greater_than)
            & LowerThanSpecification(lower_than)
            & NotEqualToSpecification(not_equal_to)
    )
    assert specification.is_satisfied(value)
