from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TimeBlock:
    code: str
    day: str
    start: str
    end: str
    block_number: int
    label: str
    priority: str = "preferred"  # preferred, iffy, optional
    is_evening: bool = False


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


BLOCKS: List[TimeBlock] = [
    TimeBlock("M1", "Monday", "08:00", "08:50", 1, "Monday 8:00-8:50"),
    TimeBlock("M2", "Monday", "09:00", "09:50", 2, "Monday 9:00-9:50"),
    TimeBlock("M3", "Monday", "10:00", "10:50", 3, "Monday 10:00-10:50"),
    TimeBlock("M4", "Monday", "11:00", "11:50", 4, "Monday 11:00-11:50"),
    TimeBlock("M5", "Monday", "12:00", "12:50", 5, "Monday 12:00-12:50"),
    TimeBlock("M6", "Monday", "13:00", "13:50", 6, "Monday 1:00-1:50"),
    TimeBlock("M7", "Monday", "14:00", "15:20", 7, "Monday 2:00-3:20"),
    TimeBlock("M8", "Monday", "15:30", "16:50", 8, "Monday 3:30-4:50"),
    TimeBlock("M9", "Monday", "17:00", "18:20", 9, "Monday 5:00-6:20"),

    TimeBlock("T21", "Tuesday", "08:00", "09:20", 21, "Tuesday 8:00-9:20"),
    TimeBlock("T22", "Tuesday", "09:30", "10:50", 22, "Tuesday 9:30-10:50"),
    TimeBlock("T23", "Tuesday", "11:00", "12:20", 23, "Tuesday 11:00-12:20"),
    TimeBlock("T24", "Tuesday", "12:30", "13:50", 24, "Tuesday 12:30-1:50"),
    TimeBlock("T25", "Tuesday", "14:00", "15:20", 25, "Tuesday 2:00-3:20"),
    TimeBlock("T26", "Tuesday", "15:30", "16:50", 26, "Tuesday 3:30-4:50"),
    TimeBlock("T27", "Tuesday", "17:00", "18:20", 27, "Tuesday 5:00-6:20"),

    TimeBlock("W1", "Wednesday", "08:00", "08:50", 1, "Wednesday 8:00-8:50"),
    TimeBlock("W2", "Wednesday", "09:00", "09:50", 2, "Wednesday 9:00-9:50"),
    TimeBlock("W3", "Wednesday", "10:00", "10:50", 3, "Wednesday 10:00-10:50"),
    TimeBlock("W4", "Wednesday", "11:00", "11:50", 4, "Wednesday 11:00-11:50"),
    TimeBlock("W5", "Wednesday", "12:00", "12:50", 5, "Wednesday 12:00-12:50"),
    TimeBlock("W6", "Wednesday", "13:00", "13:50", 6, "Wednesday 1:00-1:50"),
    TimeBlock("W7", "Wednesday", "14:00", "15:20", 7, "Wednesday 2:00-3:20", priority="iffy"),
    TimeBlock("W8", "Wednesday", "15:30", "16:50", 8, "Wednesday 3:30-4:50", priority="iffy"),
    TimeBlock("W9", "Wednesday", "17:00", "18:20", 9, "Wednesday 5:00-6:20", priority="iffy"),

    TimeBlock("R21", "Thursday", "08:00", "09:20", 21, "Thursday 8:00-9:20"),
    TimeBlock("R22", "Thursday", "09:30", "10:50", 22, "Thursday 9:30-10:50"),
    TimeBlock("R23", "Thursday", "11:00", "12:20", 23, "Thursday 11:00-12:20"),
    TimeBlock("R24", "Thursday", "12:30", "13:50", 24, "Thursday 12:30-1:50"),
    TimeBlock("R25", "Thursday", "14:00", "15:20", 25, "Thursday 2:00-3:20"),
    TimeBlock("R26", "Thursday", "15:30", "16:50", 26, "Thursday 3:30-4:50"),
    TimeBlock("R27", "Thursday", "17:00", "18:20", 27, "Thursday 5:00-6:20"),

    TimeBlock("F1", "Friday", "08:00", "08:50", 1, "Friday 8:00-8:50"),
    TimeBlock("F2", "Friday", "09:00", "09:50", 2, "Friday 9:00-9:50"),
    TimeBlock("F3", "Friday", "10:00", "10:50", 3, "Friday 10:00-10:50"),
    TimeBlock("F4", "Friday", "11:00", "11:50", 4, "Friday 11:00-11:50"),
    TimeBlock("F5", "Friday", "12:00", "12:50", 5, "Friday 12:00-12:50"),
    TimeBlock("F6", "Friday", "13:00", "13:50", 6, "Friday 1:00-1:50"),
    TimeBlock("F25", "Friday", "14:00", "15:20", 25, "Friday 2:00-3:20"),
    TimeBlock("F26", "Friday", "15:30", "16:50", 26, "Friday 3:30-4:50"),
    TimeBlock("F27", "Friday", "17:00", "18:20", 27, "Friday 5:00-6:20"),

    TimeBlock("E12", "Monday", "18:30", "21:30", 12, "Monday 6:30-9:30", priority="optional", is_evening=True),
    TimeBlock("E13", "Tuesday", "18:30", "21:30", 13, "Tuesday 6:30-9:30", priority="optional", is_evening=True),
    TimeBlock("E14", "Wednesday", "18:30", "21:30", 14, "Wednesday 6:30-9:30", priority="optional", is_evening=True),
    TimeBlock("E15", "Thursday", "18:30", "21:30", 15, "Thursday 6:30-9:30", priority="optional", is_evening=True),
]


BLOCKS_BY_CODE: Dict[str, TimeBlock] = {block.code: block for block in BLOCKS}
BLOCKS_BY_DAY_AND_TIME: Dict[tuple[str, str, str], TimeBlock] = {
    (block.day, block.start, block.end): block for block in BLOCKS
}


def get_block(code: str) -> Optional[TimeBlock]:
    return BLOCKS_BY_CODE.get(code)


def get_candidate_blocks(include_evening: bool = False, include_wednesday_iffy: bool = True) -> List[TimeBlock]:
    candidates: List[TimeBlock] = []
    for block in BLOCKS:
        if block.is_evening and not include_evening:
            continue
        if block.day == "Wednesday" and block.priority == "iffy" and not include_wednesday_iffy:
            continue
        candidates.append(block)
    return candidates


def get_block_options(include_evening: bool = True) -> List[str]:
    options: List[str] = []
    for block in BLOCKS:
        if block.is_evening and not include_evening:
            continue
        suffix = []
        if block.priority == "iffy":
            suffix.append("iffy")
        if block.is_evening:
            suffix.append("evening")
        tag = f" ({', '.join(suffix)})" if suffix else ""
        options.append(f"{block.code} - {block.label}{tag}")
    return options


def get_time_slot_options(include_evening: bool = True) -> List[str]:
    seen = set()
    options: List[str] = []

    for block in BLOCKS:
        if block.is_evening and not include_evening:
            continue

        slot = f"{block.start} - {block.end}"
        if slot not in seen:
            seen.add(slot)
            options.append(slot)

    return options


def get_block_for_day_and_time(day: str, start: str, end: str) -> Optional[TimeBlock]:
    return BLOCKS_BY_DAY_AND_TIME.get((day, start, end))


def time_to_minutes(time_str: str) -> int:
    hours, minutes = time_str.strip().split(":")
    return int(hours) * 60 + int(minutes)


def blocks_for_day_and_range(day: str, start: str, end: str, include_evening: bool = True) -> List[TimeBlock]:
    start_min = time_to_minutes(start)
    end_min = time_to_minutes(end)

    matches: List[TimeBlock] = []

    for block in BLOCKS:
        if block.day != day:
            continue
        if block.is_evening and not include_evening:
            continue

        block_start = time_to_minutes(block.start)
        block_end = time_to_minutes(block.end)

        if start_min < block_end and end_min > block_start:
            matches.append(block)

    return matches