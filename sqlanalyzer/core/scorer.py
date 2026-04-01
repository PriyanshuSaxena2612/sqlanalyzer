from dataclasses import dataclass, field
from typing import List
from dataclasses import asdict
@dataclass
class Issue:
    rule: str
    severity: str
    penalty: float
    message: str
    suggestion: str

@dataclass
class ScoreResult:
    raw_score: float = 0
    final_score: float = 0
    grade: str = "Clean"
    issues: List[Issue] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d.pop("raw_score")  # internal detail, not user facing
        return d

    def add_issue(self, issue: Issue):
        self.issues.append(issue)
        self.raw_score += issue.penalty
        self.final_score = min(100, self.raw_score)
        self.grade = self._compute_grade()

    def _compute_grade(self):
        if self.final_score <= 30:
            return "Clean"
        elif self.final_score <= 60:
            return "Moderate"
        elif self.final_score <= 85:
            return "High"
        else:
            return "Critical"