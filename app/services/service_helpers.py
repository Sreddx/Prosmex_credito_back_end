def validate_key(data, required_keys):
    """
    Verifica si todas las claves obligatorias están presentes en el diccionario `data`.

    Args:
        data (dict): Diccionario con los datos a validar.
        required_keys (list): Lista de claves obligatorias.

    Returns:
        bool: True si todas las claves están presentes, False en caso contrario.

    Raises:
        ValueError: Si alguna de las claves obligatorias falta en `data`.
    """
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise ValueError(f"Faltan las siguientes claves obligatorias: {', '.join(missing_keys)}")
    
    return True
