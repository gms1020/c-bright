from dataclasses import asdict, dataclass, field
from typing import Dict, List


CONFLICT_TYPES = ["Class", "Spring Sport", "Extracurricular", "Work", "Other"]


@dataclass
class Conflict:
    block_code: str
    conflict_type: str
    label: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Conflict":
        return cls(
            block_code=data["block_code"],
            conflict_type=data["conflict_type"],
            label=data.get("label", ""),
        )


@dataclass
class StudentResponse:
    name: str
    student_id: str
    email: str = ""
    interested: bool = True
    evening_ok: bool = False
    athlete: bool = False
    conflicts: List[Conflict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["conflicts"] = [conflict.to_dict() for conflict in self.conflicts]
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "StudentResponse":
        return cls(
            name=data.get("name", ""),
            student_id=data.get("student_id", ""),
            email=data.get("email", ""),
            interested=bool(data.get("interested", True)),
            evening_ok=bool(data.get("evening_ok", False)),
            athlete=bool(data.get("athlete", False)),
            conflicts=[Conflict.from_dict(item) for item in data.get("conflicts", [])],
        )


@dataclass
class CourseRequest:
    course_name: str = "Special Topics Course"
    include_evening: bool = False
    include_wednesday_iffy: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "CourseRequest":
        return cls(
            course_name=data.get("course_name", "Special Topics Course"),
            include_evening=bool(data.get("include_evening", False)),
            include_wednesday_iffy=bool(data.get("include_wednesday_iffy", True)),
        )
