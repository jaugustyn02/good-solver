def is_float(string):
    try:
        float_value = float(string)
        return True
    except ValueError:
        return False