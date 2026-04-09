import json
from pathlib import Path
from typing import List

from models import CourseRequest, StudentResponse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SUBMISSIONS_DIR = DATA_DIR / "submissions"
EXPORTS_DIR = DATA_DIR / "exports"
SETTINGS_PATH = DATA_DIR / "course_request.json"


for folder in (DATA_DIR, SUBMISSIONS_DIR, EXPORTS_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def clean_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value.strip())
    return cleaned.strip("_") or "student"


def save_student_response(student: StudentResponse, folder: Path = SUBMISSIONS_DIR) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{clean_filename(student.name)}_{clean_filename(student.student_id or 'id')}.json"
    path = folder / filename
    with path.open("w", encoding="utf-8") as handle:
        json.dump(student.to_dict(), handle, indent=2)
    return path


def load_student_response(path: Path) -> StudentResponse:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return StudentResponse.from_dict(data)


def load_all_student_responses(folder: Path = SUBMISSIONS_DIR) -> List[StudentResponse]:
    students: List[StudentResponse] = []
    if not folder.exists():
        return students
    for path in sorted(folder.glob("*.json")):
        students.append(load_student_response(path))
    return students


def save_course_request(course_request: CourseRequest, path: Path = SETTINGS_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(course_request.to_dict(), handle, indent=2)
    return path


def load_course_request(path: Path = SETTINGS_PATH) -> CourseRequest:
    if not path.exists():
        request = CourseRequest()
        save_course_request(request, path)
        return request
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return CourseRequest.from_dict(data)
