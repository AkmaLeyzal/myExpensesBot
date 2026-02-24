import re

CATEGORIES = {
    "🍔 Makanan": [
        "nasi", "naspad", "makan", "bakso", "mie", "ayam", "sate", "soto",
        "rendang", "nasi goreng", "martabak", "roti", "pizza", "burger",
        "sushi", "dimsum", "gorengan", "pecel", "rawon", "gudeg",
        "lauk", "sayur", "tempe", "tahu", "ikan", "udang", "cumi",
        "kebab", "rice", "rice bowl", "geprek", "seblak", "cilok",
        "batagor", "siomay", "pempek", "indomie", "mcd", "kfc",
        "warteg", "padang", "food", "snack", "cemilan", "kue",
    ],
    "☕ Minuman": [
        "kopi", "coffee", "teh", "tea", "jus", "juice", "susu", "milk",
        "air", "mineral", "boba", "chatime", "mixue", "es", "aqua",
        "minum", "latte", "cappuccino", "americano", "matcha",
        "starbucks", "sbux", "janji jiwa", "kenangan",
    ],
    "🚗 Transportasi": [
        "grab", "gojek", "uber", "taxi", "taksi", "bensin", "pertamax",
        "pertalite", "solar", "parkir", "tol", "busway", "mrt", "lrt",
        "kereta", "krl", "commuter", "ojek", "ojol", "angkot", "bus",
        "transjakarta", "tj", "transportasi", "ongkir", "kirim",
    ],
    "🛒 Belanja": [
        "baju", "sepatu", "celana", "jaket", "tas", "dompet", "jam",
        "aksesori", "gadget", "hp", "laptop", "charger", "kabel",
        "elektronik", "belanja", "shopee", "tokopedia", "lazada",
    ],
    "🏥 Kesehatan": [
        "obat", "vitamin", "dokter", "apotek", "klinik", "rumah sakit",
        "rs", "health", "masker", "sanitizer", "test", "konsul",
    ],
    "🎮 Hiburan": [
        "game", "film", "bioskop", "netflix", "spotify", "youtube",
        "nonton", "tiket", "konser", "karaoke", "main", "wisata",
    ],
    "💡 Utilitas": [
        "listrik", "pln", "wifi", "internet", "pulsa", "paket data",
        "indosat", "telkomsel", "xl", "pdam", "air pdam", "gas",
    ],
}

MULTIPLIERS = {
    "k": 1_000,
    "rb": 1_000,
    "ribu": 1_000,
    "jt": 1_000_000,
    "juta": 1_000_000,
}

PRICE_PATTERN = re.compile(
    r"^(\d+(?:[.,]\d+)?)\s*(k|rb|ribu|jt|juta)?\s+(.+)$",
    re.IGNORECASE,
)


def _parse_price(number_str: str, suffix: str | None) -> int:
    number_str = number_str.replace(",", ".")
    value = float(number_str)
    if suffix:
        multiplier = MULTIPLIERS.get(suffix.lower(), 1)
        value *= multiplier
    return int(value)


def _detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    return "📦 Lainnya"


def _split_item_description(text: str) -> tuple[str, str | None]:
    separators = [" - ", ", ", " | "]
    for sep in separators:
        if sep in text:
            parts = text.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return text.strip(), None


def parse_expense(text: str) -> dict | None:
    text = text.strip()
    if not text:
        return None

    match = PRICE_PATTERN.match(text)
    if not match:
        return None

    number_str, suffix, rest = match.groups()

    try:
        price = _parse_price(number_str, suffix)
    except (ValueError, OverflowError):
        return None

    if price <= 0:
        return None

    item, description = _split_item_description(rest)

    if not item:
        return None

    category = _detect_category(item + " " + (description or ""))

    return {
        "price": price,
        "item": item,
        "description": description,
        "category": category,
    }


def format_rupiah(amount: int) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")
