from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CodeAnalysis:
    """Detailed analysis of the code snippet."""
    quality_summary: str
    api_usage_summary: str
    best_practices_summary: str

@dataclass
class Evaluation:
    """Review of the analysis accuracy."""
    accuracy_score: float
    reviewer_comment: str

@dataclass
class AnalysisOutput:
    """The final structured output of the code analysis agent."""
    language: str
    product_name: str
    product_category: str
    analysis: CodeAnalysis
    region_tags: List[str] = field(default_factory=list)
    evaluation: Optional[Evaluation] = None
