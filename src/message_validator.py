def validate_message(message):
    """Valida si un mensaje está vacío o solo contiene espacios"""
    if not message or len(message.strip()) == 0:
        return False, b"ERROR"
    return True, b"OK"