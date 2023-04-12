from dataclasses import dataclass

import pytest

from filters.specifications import CanceledOrderBySalesChannelSpecification


@dataclass(frozen=True, slots=True)
class Item:
    type: str


@pytest.mark.parametrize(
    'sales_channel_name, other_order_types',
    [
        ('Delivery', ('Dine-In', 'Takeaway')),
        ('Dine-In', ('Delivery', 'Takeaway')),
        ('Takeaway', ('Dine-In', 'Delivery')),
    ]
)
def test_canceled_order_by_sales_channel_specification(
        sales_channel_name,
        other_order_types,
):
    specification = CanceledOrderBySalesChannelSpecification(sales_channel_name)
    item = Item(sales_channel_name)
    assert specification.is_satisfied(item)

    for order_type in other_order_types:
        item = Item(order_type)
        assert not specification.is_satisfied(item)
