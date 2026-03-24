def block_rank_key(result: dict):
    priority_penalty = {"preferred": 0, "iffy": 1, "optional": 2}.get(result.get("priority", "preferred"), 3)
    evening_penalty = 1 if result.get("is_evening", False) else 0
    student_penalty = result.get("conflict_count", 0)
    return (student_penalty, priority_penalty, evening_penalty, result.get("label", ""))
