"""Human-readable load and lint problems."""

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    """One problem. ``location`` names the node, field or section; may be empty."""

    severity: Severity
    model: str
    location: str
    message: str

    def __str__(self) -> str:
        where = f", {self.location}" if self.location else ""
        return f'{self.severity.value}: model "{self.model}"{where}: {self.message}'


class ModelError(Exception):
    """Raised when a model cannot be loaded. ``issues`` holds every error found."""

    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        super().__init__("\n".join(str(i) for i in issues))
