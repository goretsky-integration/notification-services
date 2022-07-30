from core import models, rabbitmq
from ingredient_stop_sales import db
from ingredient_stop_sales.stop_sales import get_stop_sales


def main():
    db.init_db()
    for unit_id, unit_name, stop_sales in get_stop_sales():
        ingredient_names = db.get_ingredient_names_by_unit_name(unit_name)
        ingredients = [models.IngredientStop(name=stop_sale.ingredient_name, reason=stop_sale.reason,
                                             started_at=stop_sale.started_at)
                       for stop_sale in stop_sales
                       if (stop_sale.ingredient_name not in ingredient_names)
                       and (stop_sale.staff_name_who_resumed is None)]
        if not ingredients:
            continue
        payload = models.StopSalesByOtherIngredients(ingredients=ingredients, unit_name=unit_name)
        rabbitmq.add_notification_to_queue({
            'type': 'STOPS_AND_RESUMES',
            'unit_id': unit_id,
            'payload': payload.dict(),
        })
        new_ingredient_names = (ingredient.name for ingredient in ingredients)
        db.add_ingredient_names(unit_name, *new_ingredient_names)


if __name__ == '__main__':
    main()
