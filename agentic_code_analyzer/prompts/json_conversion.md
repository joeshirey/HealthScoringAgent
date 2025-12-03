# JSON Conversion

Your task is to convert the following text analysis of a code sample into a single, valid JSON object that strictly conforms to the provided JSON schema.

**JSON Schema:**

```json
{
  "overall_compliance_score": "integer (0-100)",
  "criteria_breakdown": [
    {
      "criterion_name": "'runnability_and_configuration' | 'api_effectiveness_and_correctness' | 'comments_and_code_clarity' | 'formatting_and_consistency' | 'language_best_practices' | 'llm_training_fitness_and_explicitness'",
      "score": "integer (0-100)",
      "weight": "float",
      "assessment": "string",
      "assessment_details": "Union[str, RunnabilityChecks, List[ApiCallAnalysis]]",
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
```

---

## CRITICAL INSTRUCTIONS FOR `assessment` FIELD

The content of the `assessment` string for each criterion MUST follow these rules:

1. **Concise Summary:** The `assessment` text must be a concise, standalone summary. It should be detailed enough for a developer to understand the key findings and their impact without needing to read the `assessment_details` field, but **avoid excessive verbosity** to ensure the entire JSON response fits within the output token limit.
2. **Professional Tone:** Write clearly and professionally.
3. **Incorporate Citations:** For the `runnability_and_configuration` and `api_effectiveness_and_correctness` criteria, you **MUST** embed citations directly into the `assessment` summary text. Use the format `[citation_number]` to support claims about best practices, API existence, or configuration standards. Link these numbers to the corresponding entries in the top-level `citations` list.
4. **Be Specific:** Mention specific issues, like hardcoded values or missing error handling. If the analysis provides line numbers for critical issues (like in `api_effectiveness_and_correctness`), reference them in the assessment text.

**Example of a good `assessment` string for `api_effectiveness_and_correctness`:**
"The API usage suffers from two major flaws. First, the `ModelArmorClient` constructor at line 45 is instantiated with a manually constructed `apiEndpoint`. This is not the standard or correct way to specify a regional endpoint for Google Cloud client libraries, which typically handle this automatically via client configuration options [8, 10]. Second, and more critically, the asynchronous `client.createTemplate(request)` call at line 88 lacks any error handling. A failure in this API call, due to network issues or invalid input, would result in an unhandled promise rejection and cause the entire process to crash. While the methods being used are valid parts of the API [1, 2, 3, 8], these implementation errors make the API usage incorrect and unreliable."

---

**TEXT TO CONVERT:**
{{initial_analysis_output}}
