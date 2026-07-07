from typing import List

from pydantic import BaseModel, field_validator


class SummaryReport(BaseModel):
    titre: str
    resume: str
    points_cles: List[str] = []
    decisions: List[str] = []
    actions: List[str] = []

    @field_validator("decisions", "actions", mode="before")
    @classmethod
    def _normalize_null_marker(cls, value):
        if value is None or value == "null":
            return []
        if isinstance(value, list):
            return value
        return [value]
