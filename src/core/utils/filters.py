def is_valid_ingredient(ingredient_name: str) -> bool:
    ingredient_name = ingredient_name.lower().strip()
    valid_ingredient_names = [["моцарелла"], ["пицца", "соус"], ["тесто"]]
    for valid_ingredient_name_parts in valid_ingredient_names:
        if all((valid_name_part in ingredient_name for valid_name_part in valid_ingredient_name_parts)):
            return True
    return False
