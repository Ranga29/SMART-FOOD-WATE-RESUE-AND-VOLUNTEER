from datetime import datetime, timezone

AVERAGE_URBAN_SPEED_KMH = 25.0
HANDLING_BUFFER_MINUTES = 15.0

def validate_safe_transit(distance_km: float, expiry_time: datetime) -> dict:
    """
    Validates if food reaches destination before spoilage.
    Formula: Estimated Travel Time + Handling Buffer < Remaining Shelf Life
    """
    now = datetime.now(timezone.utc)
    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)
    else:
        expiry_time = expiry_time.astimezone(timezone.utc)
    remaining_shelf_life_min = (expiry_time - now).total_seconds() / 60.0

    estimated_travel_min = (distance_km / AVERAGE_URBAN_SPEED_KMH) * 60.0
    total_required_min = estimated_travel_min + HANDLING_BUFFER_MINUTES

    is_safe = total_required_min < remaining_shelf_life_min

    return {
        "is_safe": is_safe,
        "estimated_travel_minutes": round(estimated_travel_min, 1),
        "total_required_minutes": round(total_required_min, 1),
        "remaining_shelf_life_minutes": round(remaining_shelf_life_min, 1),
    }