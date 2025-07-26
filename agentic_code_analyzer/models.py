from pydantic import BaseModel, Field, conint
from typing import List, Literal, Union

# Defining specific literals for criterion names to enforce consistency
CriterionName = Literal[
    'runnability_and_configuration',
    'api_effectiveness_and_correctness',
    'comments_and_code_clarity',
    'formatting_and_consistency',
    'language_best_practices',
    'llm_training_fitness_and_explicitness'
]

# --- Structured Assessment Models ---

class SyntaxValidity(BaseModel):
    is_valid: bool
    reasoning: str

class DependencyManagement(BaseModel):
    has_dependencies: bool
    are_declared: Literal['Yes', 'No', 'NA']
    reasoning: str

class ConfigurationManagement(BaseModel):
    uses_env_vars: bool
    are_documented: Literal['Yes', 'No', 'NA']
    reasoning: str

class HardcodedValues(BaseModel):
    contains_hardcoded_values: bool
    details: str

class RunnabilityChecks(BaseModel):
    syntax_validity: SyntaxValidity
    dependency_management: DependencyManagement
    configuration_management: ConfigurationManagement
    hardcoded_values: HardcodedValues

class ApiEvaluationDetail(BaseModel):
    status: Literal['Pass', 'Fail', 'NA']
    reasoning: str

class ApiCallEvaluation(BaseModel):
    method_existence_check: ApiEvaluationDetail
    parameter_check: ApiEvaluationDetail
    response_handling_check: ApiEvaluationDetail
    error_handling_check: ApiEvaluationDetail

class ApiCallAnalysis(BaseModel):
    method_name: str
    line_number: int
    evaluation: ApiCallEvaluation

# --- Main Evaluation Schema ---

class CriteriaBreakdown(BaseModel):
    """Pydantic model for the criteria breakdown in the final evaluation."""
    criterion_name: CriterionName = Field(..., description="The name of the criterion being assessed.")
    score: conint(ge=0, le=100) = Field(..., description="The score for this criterion, from 0 to 100.")
    weight: float = Field(..., description="The weight of this criterion in the overall score.")
    assessment: Union[str, RunnabilityChecks, List[ApiCallAnalysis]] = Field(..., description="The detailed assessment, which can be a string or a structured object for specific criteria.")
    recommendations_for_llm_fix: List[str] = Field(default=[], description="Actionable recommendations for an LLM to fix issues.")
    generic_problem_categories: List[str] = Field(default=[], description="Generic categories of the identified problems.")

class Citation(BaseModel):
    """Pydantic model for a citation."""
    citation_number: int = Field(..., description="The number of the citation.")
    url: str = Field(..., description="The URL of the citation.")

class EvaluationOutput(BaseModel):
    """Pydantic model for the final output of the evaluation workflow."""
    overall_compliance_score: conint(ge=0, le=100) = Field(..., description="The overall compliance score for the code sample.")
    criteria_breakdown: List[CriteriaBreakdown] = Field(..., min_items=1, description="A breakdown of the score by criterion.")
    llm_fix_summary_for_code_generation: List[str] = Field(default=[], description="A summary of the fixes an LLM could make.")
    identified_generic_problem_categories: List[str] = Field(default=[], description="The unique generic categories of the identified problems.")
    citations: List[Citation] = Field(default=[], description="A list of citations for the analysis.")
