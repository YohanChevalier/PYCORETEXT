def _criteria_to_string(dico: dict):
    """Prend le dictionnaire des critères et renvoit une string"""
    final_string = ""
    list_keys = list(dico.keys())
    for index, key in enumerate(list_keys):
        final_string += f"{key} : {dico[key]}"
        if index in [3, 7, 11]:
            final_string += "\n"
        else:
            final_string += " / "
    return final_string


dico = {
    1: "a",
    2: "b",
    3: "c",
    4: "d",
    5: "e",
    6: "f",
    7: "g",
    8: "h",
    9: "i",
    10: "j"
}

print(_criteria_to_string(dico))
