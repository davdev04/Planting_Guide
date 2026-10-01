import re


def sanitise_name(name: object) -> str:
    if name is None:
        raise ValueError("Plant name is required.")

    cleaned = str(name).strip()
    if not cleaned:
        raise ValueError("Plant name is required.")

    if len(cleaned) > 80:
        raise ValueError("Plant name is too long.")

    if any(ord(ch) < 32 for ch in cleaned):
        raise ValueError("Plant name contains invalid control characters.")

    disallowed = {";", "|", "&", "$", "`", "<", ">", "\n", "\r", "\t"}
    if any(ch in cleaned for ch in disallowed):
        raise ValueError("Plant name contains invalid characters.")

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9\s'\-.]*", cleaned):
        raise ValueError("Plant name contains unsupported characters.")

    return cleaned


def normalise_planting_age(planting_age: object | None) -> str:
    if planting_age is None:
        return "seed"

    value = getattr(planting_age, "value", planting_age)
    cleaned = str(value).strip().lower()

    if not cleaned:
        return "seed"

    if cleaned not in {"seed", "seedling"}:
        raise ValueError("planting_age must be 'seed' or 'seedling'.")

    return cleaned
