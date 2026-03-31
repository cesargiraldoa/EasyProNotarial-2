from datetime import datetime, timedelta, timezone

BOGOTA_TIME_ZONE = timezone(timedelta(hours=-5), name="America/Bogota")


def assume_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_bogota(value: datetime | None) -> datetime | None:
    normalized = assume_utc(value)
    if normalized is None:
        return None
    return normalized.astimezone(BOGOTA_TIME_ZONE)


def format_bogota_datetime(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M") -> str | None:
    localized = to_bogota(value)
    if localized is None:
        return None
    return localized.strftime(fmt)
