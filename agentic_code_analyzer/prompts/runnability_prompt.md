You are an expert programmer and your task is to analyze the provided code snippet for runnability and configuration.

**LANGUAGE:**
{{language}}

**CODE SNIPPET:**
```{{language}}
{{code_snippet}}
```

**CRITERIA:**

**Runnability & Configuration (Weight: 0.15)**

*   Is the code runnable by default?
*   Assume that declared dependencies are valid and exist.
*   Does it use minimum parameters, reserving them for environmental configuration?
*   Are all prerequisite configurations or variable settings clearly indicated?
*   Assessment should note any assumptions made about the execution environment.

**OUTPUT FORMAT:**

Provide your analysis in a JSON format with the following structure:

```json
{
  "runnability_assessment": {
    "score": "integer (0-100)",
    "assessment": "string"
  }
}
```
