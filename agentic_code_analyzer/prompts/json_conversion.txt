Your task is to convert the following text into a valid JSON object that conforms to the following schema:

{
  "overall_compliance_score": "integer (0-100)",
  "criteria_breakdown": [
    {
      "criterion_name": "'runnability_and_configuration' | 'api_effectiveness_and_correctness' | 'comments_and_code_clarity' | 'formatting_and_consistency' | 'language_best_practices' | 'llm_training_fitness_and_explicitness'",
      "score": "integer (0-100)",
      "weight": "float",
      "assessment": "Union[str, RunnabilityChecks, List[ApiCallAnalysis]]",
      "recommendations_for_llm_fix": ["string"],
      "generic_problem_categories": ["string"]
    }
  ],
  "llm_fix_summary_for_code_generation": ["string"],
  "identified_generic_problem_categories": ["string"],
  "citations": [
    {
      "citation_number": "integer",
      "url": "string"
    }
  ]
}

**TEXT TO CONVERT:**
{{initial_analysis_output}}
