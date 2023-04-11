import datetime
from dataclasses import dataclass

from filters.specifications import CanceledOrderHasPrintedReceiptSpecification


@dataclass(frozen=True, slots=True)
class Item:
    receipt_printed_at: datetime.datetime | None


def test_canceled_order_has_printed_receipt_specification(faker):
    specification = CanceledOrderHasPrintedReceiptSpecification()

    item = Item(receipt_printed_at=faker.date_time())
    assert specification.is_satisfied(item)

    item = Item(receipt_printed_at=None)
    assert not specification.is_satisfied(item)
