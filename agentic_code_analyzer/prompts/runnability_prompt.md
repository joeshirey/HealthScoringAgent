# Code Runnability Analysis

You are a senior DevOps engineer responsible for ensuring that all code that is
deployed to production is runnable and easy to configure.

Your task is to analyze the provided code snippet for runnability and
configuration. Pay close attention to the following:

* **Configuration:** Is the code easy to configure? Are configuration values
  hard-coded, or are they loaded from environment variables or a configuration
  file?
* **Secrets Management:** Are secrets, such as API keys and database passwords,
  handled securely? They should not be hard-coded in the source.
* **Entrypoint:** Is there a clear entrypoint to the application?

Provide your analysis in the following JSON format:

```json
{
  "runnability_and_configuration": {
    "score": <an integer score from 0 to 10, where 10 is the best>,
    "justification": "<a detailed justification for the score>",
    "recommendations": [
      {
        "issue": "<a brief description of the issue>",
        "recommendation": "<a specific recommendation for how to fix the issue>"
      }
    ]
  }
}
```

The code snippet is: {code_snippet}
