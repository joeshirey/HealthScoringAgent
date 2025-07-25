# HealthScoringAgent

The HealthScoringAgent is a sophisticated, multi-agent system designed to analyze and evaluate code samples for quality, correctness, and adherence to best practices. It uses a combination of rules-based logic and large language models (LLMs) to provide a comprehensive and nuanced assessment of code health.

## Key Features

*   **Multi-Agent Architecture:** The system is built on a modular, multi-agent architecture, where each agent is responsible for a specific aspect of the analysis. This allows for a clear separation of concerns and makes the system easy to extend and maintain.
*   **Two-Step Evaluation Process:** The evaluation process is divided into two steps. The first step performs a detailed analysis of the code, using web grounding to ensure the information is accurate and up-to-date. The second step formats the analysis into a clean, structured JSON object.
*   **Advanced Product Categorization:** The system uses a sophisticated, rules-based product categorization engine with an LLM fallback. This allows for accurate and reliable categorization of code samples, even in ambiguous cases.
*   **Detailed System Instructions:** The LLMs are guided by a detailed set of system instructions that define their persona, workflow, and the criteria for their analysis. This ensures that the analysis is consistent, rigorous, and aligned with the project's goals.
*   **Code Cleaning:** The system includes a utility to remove comments from the code before analysis. This ensures that the analysis is focused on the executable code and is not influenced by comments.

## Getting Started

To get started with the HealthScoringAgent, you will need to have Python 3.12 or higher installed. You will also need to have a Google Cloud project with the Vertex AI API enabled.

1.  **Clone the repository:**
    ```
    git clone https://github.com/joeshirey/HealthScoringAgent.git
    ```
2.  **Create a virtual environment:**
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install the dependencies:**
    ```
    uv pip install -r agentic_code_analyzer/requirements.txt
    ```
4.  **Run the application:**
    ```
    uv run -m agentic_code_analyzer.main
    ```

## Project Structure

The project is organized into the following directories:

*   `agentic_code_analyzer/`: The main application directory.
    *   `agents/`: Contains the individual agents that make up the system.
    *   `prompts/`: Contains the prompt templates that are used to guide the LLMs.
    *   `tools/`: Contains the tools and utilities that are used by the agents.
*   `docs/`: Contains the project documentation.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more information.