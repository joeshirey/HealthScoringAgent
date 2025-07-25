from pydantic import BaseModel, Field
from typing import List

class AnalysisOutput(BaseModel):
    """A standardized model for the output of individual analysis agents."""
    score: int = Field(..., description="The score from 1-10 for the analysis category.")
    summary: str = Field(..., description="A brief, high-level summary of the findings.")
    details: List[str] = Field(..., description="A list of specific observations, issues, or recommendations.")

class CodeQualityOutput(AnalysisOutput):
    """Pydantic model for the output of the CodeQualityAgent."""
    pass

class ClarityReadabilityOutput(AnalysisOutput):
    """Pydantic model for the output of the ClarityReadabilityAgent."""
    pass

class RunnabilityOutput(AnalysisOutput):
    """Pydantic model for the output of the RunnabilityAgent."""
    pass

class ApiAnalysisOutput(AnalysisOutput):
    """Pydantic model for the output of the ApiAnalysisAgent."""
    pass

class CriteriaBreakdown(BaseModel):
    """Pydantic model for the criteria breakdown in the final evaluation."""
    criterion_name: str = Field(..., description="The name of the criterion being assessed.")
    score: int = Field(..., description="The score for this criterion.")
    weight: float = Field(..., description="The weight of this criterion in the overall score.")
    assessment: str = Field(..., description="The assessment of the code against this criterion.")
    recommendations_for_llm_fix: List[str] = Field(..., description="Recommendations for how an LLM could fix the issues.")
    generic_problem_categories: List[str] = Field(..., description="The generic categories of the identified problems.")

class Citation(BaseModel):
    """Pydantic model for a citation."""
    citation_number: int = Field(..., description="The number of the citation.")
    url: str = Field(..., description="The URL of the citation.")

class EvaluationOutput(BaseModel):
    """Pydantic model for the final output of the evaluation workflow."""
    product_category: str = Field(..., description="The product category of the code sample.")
    product_name: str = Field(..., description="The product name of the code sample.")
    overall_compliance_score: int = Field(..., description="The overall compliance score for the code sample.")
    criteria_breakdown: List[CriteriaBreakdown] = Field(..., description="A breakdown of the score by criterion.")
    llm_fix_summary_for_code_generation: List[str] = Field(..., description="A summary of the fixes an LLM could make.")
    identified_generic_problem_categories: List[str] = Field(..., description="The generic categories of the identified problems.")
    citations: List[Citation] = Field(..., description="A list of citations for the analysis.")
