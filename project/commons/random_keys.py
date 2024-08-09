import uuid


def generate_unique_id() -> str:
    """
    Generate a unique identifier using UUID4.

    Returns:
        str: A unique identifier as a string.
    """
    return str(uuid.uuid4())
