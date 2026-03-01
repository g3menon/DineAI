from typing import Any, Optional


def parse_price(raw_price: Any) -> Optional[float]:
    """
    Convert a raw price value like "1,500" or "₹1,500" into a simple number (e.g. 1500).

    Returns:
        float or None: Parsed price, or None if parsing fails.
    """
    if raw_price is None:
        return None

    # If it's already a number, just return it as float.
    if isinstance(raw_price, (int, float)):
        return float(raw_price)

    text = str(raw_price)
    # Remove currency symbols and commas commonly found in prices.
    cleaned = (
        text.replace("₹", "")
        .replace(",", "")
        .replace("INR", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_rating(raw_rating: Any) -> Optional[float]:
    """
    Convert a raw rating like "4.1/5" or "4.1" into a float (e.g. 4.1).

    Returns:
        float or None: Parsed rating, or None if parsing fails.
    """
    if raw_rating is None:
        return None

    if isinstance(raw_rating, (int, float)):
        return float(raw_rating)

    text = str(raw_rating).strip()

    # If it contains "/", keep only the part before the slash.
    if "/" in text:
        text = text.split("/", maxsplit=1)[0]

    try:
        return float(text)
    except ValueError:
        return None

