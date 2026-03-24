from collections import Counter
from typing import Dict, List

from models import CourseRequest, StudentResponse
from ranking import block_rank_key
from time_blocks import get_block, get_candidate_blocks


def analyze_schedules(students: List[StudentResponse], course_request: CourseRequest) -> List[Dict]:
    candidates = get_candidate_blocks(
        include_evening=course_request.include_evening,
        include_wednesday_iffy=course_request.include_wednesday_iffy,
    )
    interested_students = [student for student in students if student.interested]

    results: List[Dict] = []
    for block in candidates:
        conflict_details = []
        type_counter = Counter()
        for student in interested_students:
            matched_conflicts = [conflict for conflict in student.conflicts if conflict.block_code == block.code]
            if block.is_evening and student.evening_ok:
                matched_conflicts = []
            if matched_conflicts:
                for conflict in matched_conflicts:
                    type_counter[conflict.conflict_type] += 1
                    conflict_details.append({
                        "student": student.name,
                        "student_id": student.student_id,
                        "conflict_type": conflict.conflict_type,
                        "label": conflict.label,
                    })

        available_count = len(interested_students) - len({item['student_id'] or item['student'] for item in conflict_details})
        results.append({
            "block_code": block.code,
            "label": block.label,
            "day": block.day,
            "start": block.start,
            "end": block.end,
            "priority": block.priority,
            "is_evening": block.is_evening,
            "conflict_count": len({item['student_id'] or item['student'] for item in conflict_details}),
            "available_count": available_count,
            "conflict_types": dict(type_counter),
            "conflicts": conflict_details,
        })

    results.sort(key=block_rank_key)
    return results


def summarize_block(block_code: str, students: List[StudentResponse]) -> Dict:
    block = get_block(block_code)
    if block is None:
        raise ValueError(f"Unknown block code: {block_code}")
    matches = []
    for student in students:
        for conflict in student.conflicts:
            if conflict.block_code == block_code:
                matches.append({
                    "student": student.name,
                    "conflict_type": conflict.conflict_type,
                    "label": conflict.label,
                })
    return {
        "block_code": block.code,
        "label": block.label,
        "priority": block.priority,
        "matches": matches,
    }
