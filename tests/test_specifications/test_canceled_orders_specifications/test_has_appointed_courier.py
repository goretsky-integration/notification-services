from dataclasses import dataclass

from filters.specifications import CanceledOrderHasAppointedCourierSpecification


@dataclass(frozen=True, slots=True)
class Item:
    courier_name: str | None


def test_canceled_order_has_appointed_courier_specification(faker):
    specification = CanceledOrderHasAppointedCourierSpecification()

    item = Item(courier_name=faker.name())
    assert specification.is_satisfied(item)

    item = Item(courier_name=None)
    assert not specification.is_satisfied(item)
