from typing import List, Dict

def split_bulk_surplus(total_servings: int, shelter_demands: List[Dict[str, int]]) -> List[Dict]:
    allocations = []
    remaining = total_servings

    sorted_demands = sorted(shelter_demands, key=lambda x: x["demand"])

    for item in sorted_demands:
        if remaining <= 0:
            break
        granted = min(remaining, item["demand"])
        allocations.append({
            "shelter_id": item["shelter_id"],
            "allocated_servings": granted
        })
        remaining -= granted

    return allocations