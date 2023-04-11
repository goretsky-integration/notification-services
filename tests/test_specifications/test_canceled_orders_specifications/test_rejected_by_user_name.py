from dataclasses import dataclass

from filters.specifications import CanceledOrderRejectedByUserNameSpecification


@dataclass(frozen=True, slots=True)
class Item:
    rejected_by_user_name: str | None


def test_canceled_order_rejected_by_user_name_specification(faker):
    specification = CanceledOrderRejectedByUserNameSpecification()

    item = Item(rejected_by_user_name=faker.name())
    assert specification.is_satisfied(item)

    item = Item(rejected_by_user_name=None)
    assert not specification.is_satisfied(item)
