You are an expert programmer and your task is to analyze the provided code snippet for API effectiveness and correctness.

**LANGUAGE:**
{{language}}

**CODE SNIPPET:**
```{{language}}
{{code_snippet}}
```

**CRITERIA:**

**API Effectiveness & Correctness (Weight: 0.40)**

*   For EACH method call in the code, you MUST explicitly state in your assessment whether its parameter structure is correct according to the official documentation.
*   Verify that the code correctly handles the **actual structure and data types** of API responses.
*   Your entire API assessment MUST be based on the official documentation for the specified language.
*   You MUST validate that all client libraries, methods, parameters, and properties are public and used correctly.
*   Does the sample implement rudimentary error handling (try/catch, err != nil, etc.)?

**OUTPUT FORMAT:**

Provide your analysis in a JSON format with the following structure:

```json
{
  "api_analysis_assessment": {
    "score": "integer (0-100)",
    "assessment": "string",
    "recommendations_for_llm_fix": ["string"],
    "generic_problem_categories": ["string"]
  }
}
```
