You are an expert programmer and your task is to analyze the provided code snippet for code quality, including formatting, consistency, and adherence to language best practices.

**LANGUAGE:**
{{language}}

**CODE SNIPPET:**
```{{language}}
{{code_snippet}}
```

**CRITERIA:**

1.  **Formatting & Consistency (Weight: 0.10)**
    *   Is the code formatting consistent within the sample?
    *   Does it adhere to the canonical style guide for **{{language}}**?

2.  **Language Best Practices (Weight: 0.15)**
    *   Does the code follow idiomatic constructs for **{{language}}**?
    *   Does it avoid anti-patterns or deprecated features?
    *   Does it avoid language features that are newer than the previous major version of the language?
    *   Does it prefer using libraries bundled in the standard library over external dependencies where applicable?

**OUTPUT FORMAT:**

Provide your analysis in a JSON format with the following structure:

```json
{
  "code_quality_assessment": {
    "formatting_and_consistency": {
      "score": "integer (0-100)",
      "assessment": "string"
    },
    "language_best_practices": {
      "score": "integer (0-100)",
      "assessment": "string"
    }
  }
}
```
