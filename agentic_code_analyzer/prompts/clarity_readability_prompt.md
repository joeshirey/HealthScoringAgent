You are an expert programmer and your task is to analyze the provided code snippet for clarity, readability, and fitness for LLM training.

**LANGUAGE:**
{{language}}

**CODE SNIPPET:**
```{{language}}
{{code_snippet}}
```

**CRITERIA:**

1.  **Comments & Code Clarity (Weight: 0.10)**
    *   Are comments helpful and explanatory, clarifying the "why" behind non-obvious code?
    *   Is the code itself clear, readable, and easy to understand?
    *   Does the sample effectively teach a developer how to perform a specific action with the API?

2.  **LLM Training Fitness & Explicitness (Weight: 0.10)**
    *   Is the code explicit and self-documenting? It MUST avoid "magic values" and favor descriptive variable names.
    *   Does the sample use type hints or explicit type declarations where idiomatic for the language?
    *   Is the demonstrated pattern clear and unambiguous, providing a strong, positive example for an LLM to learn from?

**OUTPUT FORMAT:**

Provide your analysis in a JSON format with the following structure:

```json
{
  "clarity_and_readability_assessment": {
    "comments_and_code_clarity": {
      "score": "integer (0-100)",
      "assessment": "string"
    },
    "llm_training_fitness_and_explicitness": {
      "score": "integer (0-100)",
      "assessment": "string"
    }
  }
}
```
