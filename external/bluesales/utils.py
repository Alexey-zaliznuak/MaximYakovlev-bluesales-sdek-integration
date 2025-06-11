SEPARATOR = "."

def get_property_safely(obj, property_path: str, on_fail):
    for property in property_path.split(SEPARATOR):
        if hasattr(obj, "get"):
            obj = obj.get(property, on_fail)
            continue

        return on_fail

    return obj
