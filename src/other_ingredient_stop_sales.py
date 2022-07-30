from core import models, rabbitmq
from ingredient_stop_sales.stop_sales import get_stop_sales


def main():
    for unit_id, unit_name, stop_sales in get_stop_sales():
        ingredients = [models.IngredientStop(name=stop_sale.ingredient_name, reason=stop_sale.reason,
                                             started_at=stop_sale.started_at)
                       for stop_sale in stop_sales
                       if stop_sale.staff_name_who_resumed is None]
        payload = models.StopSalesByOtherIngredients(ingredients=ingredients, unit_name=unit_name)
        rabbitmq.add_notification_to_queue({
            'type': 'STOPS_AND_RESUMES',
            'unit_id': unit_id,
            'payload': payload.dict(),
        })


if __name__ == '__main__':
    main()
