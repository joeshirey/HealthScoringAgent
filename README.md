# Health Scoring Agent

The Health Scoring Agent is a sophisticated, multi-agent system designed to analyze and evaluate code samples for quality, correctness, and adherence to best practices. It uses a combination of rules-based logic and large language models (LLMs) to provide a comprehensive and nuanced assessment of code health.

## 📖 Table of Contents

- [Health Scoring Agent](#health-scoring-agent)
  - [📖 Table of Contents](#-table-of-contents)
  - [✨ Key Features](#-key-features)
  - [🏗️ System Architecture](#️-system-architecture)
    - [Orchestrator](#orchestrator)
    - [Agents](#agents)
    - [Tools](#tools)
  - [🚀 Getting Started](#-getting-started)
  - [↔️ API Reference](#️-api-reference)
    - [`POST /analyze`](#post-analyze)
    - [`POST /analyze_github_link`](#post-analyze_github_link)
  - [📁 Project Structure](#-project-structure)
  - [🤝 Contributing](#-contributing)

## ✨ Key Features

- **Multi-Agent Architecture:** The system is built on a modular, multi-agent architecture, where each agent is responsible for a specific aspect of the analysis. This allows for a clear separation of concerns and makes the system easy to extend and maintain.
- **Two-Step Evaluation Process:** The evaluation process is divided into two steps. The first step performs a detailed analysis of the code, using web grounding to ensure the information is accurate and up-to-date. The second step formats the analysis into a clean, structured JSON object.
- **Advanced Prompt Engineering:** The LLMs are guided by meticulously engineered prompts that establish specific personas (e.g., "Principal Engineer," "Senior DevOps Engineer"), provide detailed context and instructions, and specify a structured output format. This results in more consistent, accurate, and actionable analysis.
- **Advanced Product Categorization:** The system uses a sophisticated, rules-based product categorization engine with an LLM fallback. This allows for accurate and reliable categorization of code samples, even in ambiguous cases.
- **Code Cleaning:** The system includes a utility to remove comments from the code before analysis. This ensures that the analysis is focused on the executable code and is not influenced by comments.
- **Web Interface:** The project includes a simple web interface for submitting code samples for analysis. The interface provides a user-friendly way to interact with the system and view the results of the analysis.
- **Self-Validation Workflow:** Includes a secondary, independent agentic workflow designed to validate the output of the primary analysis. This "peer review" model uses Google Search to verify the claims made by the initial evaluation, adding a robust layer of quality control and increasing the reliability of the final score.
- **Iterative Refinement:** The system is designed to pursue high-quality analysis through a feedback loop. It can be configured to re-run the entire analysis if the validation agent's score for the analysis is below a set threshold (e.g., 7 out of 10). The reasoning from the validation is passed back to the analysis agent as constructive feedback, allowing it to refine its evaluation in the next iteration. This process continues until the analysis is deemed high-quality or a configurable maximum number of attempts is reached.

## 🏗️ System Architecture

The Health Scoring Agent is built on a multi-agent architecture that is designed to be modular, extensible, and maintainable. The system is composed of the following key components:

### Orchestrator

The `CodeAnalyzerOrchestrator` is the heart of the system. It is responsible for coordinating the workflow of the various agents and ensuring that the analysis is performed in the correct order. The orchestrator uses a sequential agent to manage the overall flow of the analysis, which is divided into the following three phases:

1.  **Initial Analysis:** In this phase, a parallel agent is used to perform a set of initial analysis tasks, including language detection and region tag extraction.
2.  **Evaluation:** In this phase, a sequential agent is used to perform a two-step evaluation of the code. The first step uses an `InitialAnalysisAgent` to perform a detailed analysis of the code, and the second step uses a `JsonFormattingAgent` to format the analysis into a structured JSON object.
3.  **Result Processing:** In this phase, a `ResultProcessingAgent` is used to process the results of the analysis, enforce the single penalty rule, and format the final output.
4.  **Iterative Validation and Refinement (API Layer):** After the primary analysis is complete, the API triggers a secondary, independent `ValidationOrchestrator`. This orchestrator also uses a two-step process:
    *   An `EvaluationVerificationAgent` uses the `google_search` tool to verify the claims made in the original evaluation, focusing on API correctness. It produces a raw text analysis of its findings.
    *   A `ValidationFormattingAgent` takes this raw text and structures it into a final validation score and reasoning.
    *   If the validation score is below a configurable threshold (default is 7), the API will re-run the entire analysis, passing the reasoning from the validation agent as feedback to the `CodeAnalyzerOrchestrator`. This loop continues until the validation score is acceptable or a maximum number of loops is reached.

### Agents

The system is composed of a variety of agents, each of which is responsible for a specific aspect of the analysis. The agents are organized into the following categories:

- **Analysis Agents:** These agents are responsible for performing the core analysis of the code. They include agents for analyzing code quality, runnability, and API effectiveness.
- **Categorization Agents:** These agents are responsible for categorizing the code sample. They include agents for detecting the language, extracting region tags, and identifying the product.
- **Formatting Agents:** These agents are responsible for formatting the output of the analysis. They include an agent for converting the raw analysis into a structured JSON object.

### Tools

The agents use a variety of tools to perform their analysis. These tools include:

- **Code Cleaning:** A utility to remove comments from the code before analysis.
- **Product Categorization:** A sophisticated, rules-based product categorization engine with an LLM fallback.
- **Google Search:** A tool to perform web searches to gather information about APIs and best practices.

## 🚀 Getting Started

To get started with the Health Scoring Agent, you will need to have Python 3.12 or higher installed. You will also need to have a Google Cloud project with the Vertex AI API enabled.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/joeshirey/HealthScoringAgent.git
    cd HealthScoringAgent
    ```

2.  **Create a virtual environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**

    The project uses `uv` for fast dependency management. The dependencies are listed in the `pyproject.toml` file.

    ```bash
    uv pip install -e .
    ```

4.  **Set up your environment variables:**

    The application requires API keys for Google AI services. A sample environment file is provided.

    ```bash
    # Copy the sample environment file
    cp .env.sample .env
    ```

    Now, open the `.env` file and add your API key:

    ```bash
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    GEMINI_PRO_MODEL="gemini-2.5-pro"
    GEMINI_FLASH_LITE_MODEL="gemini-2.5-flash-lite"
    MAX_VALIDATION_LOOPS=3
    ```

5.  **Run the application:**

    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8090
    ```

## ↔️ API Reference

The Health Scoring Agent provides a simple REST API for analyzing code samples.

### `POST /analyze`

Analyzes a code sample and returns a detailed analysis of its health.

**Request Body:**

- `code` (string, required): The code sample to analyze.
- `github_link` (string, optional): The GitHub link to the code sample.

**Response Body:**

A JSON object containing the detailed analysis and a history of the validation attempts.

- `analysis`: The full, detailed health score analysis from the final iteration of the agent workflow.
- `validation_history`: A list of objects, where each object represents a validation attempt and contains:
  - `validation_score`: A score from 1-10 on the quality of the analysis.
  - `reasoning`: A detailed explanation for the validation score.

**Example:**

```bash
curl -X POST http://0.0.0.0:8090/analyze \
-H "Content-Type: application/json" \
-d '{
    "code": "def hello_world():\n    print(\"Hello, world!\")"
}'
```

### `POST /analyze_github_link`

Analyzes a code sample from a GitHub link and returns a detailed analysis of its health.

**Request Body:**

- `github_link` (string, required): The GitHub link to the code sample.

**Example:**

```bash
curl -X POST http://0.0.0.0:8090/analyze_github_link \
-H "Content-Type: application/json" \
-d '{
    "github_link": "https://github.com/googleapis/google-cloud-node/blob/main/packages/google-cloud-alloydb/samples/quickstart.js"
}'
```

### `POST /validate`

Validates an existing evaluation against the source code from a GitHub link.

**Request Body:**

- `github_link` (string, required): The GitHub link to the code sample.
- `evaluation` (object, required): The JSON object from a previous analysis.

**Response Body:**

A JSON object containing the validation score and reasoning.

- `validation_score`: A score from 1-10 on the quality of the analysis.
- `reasoning`: A detailed explanation for the validation score.

**Example:**

```bash
curl -X POST http://0.0.0.0:8090/validate \
-H "Content-Type: application/json" \
-d '{
    "github_link": "https://github.com/googleapis/google-cloud-node/blob/main/packages/google-cloud-alloydb/samples/quickstart.js",
    "evaluation": { ... }
}'
```

## 📁 Project Structure

```

The project is organized into the following directories:

- `agentic_code_analyzer/`: The main application directory.
  - `agents/`: Contains the individual agents that make up the system.
  - `prompts/`: Contains the prompt templates that are used to guide the LLMs. These prompts are engineered to provide clear instructions, establish a specific persona for the LLM, and define the expected output format.
  - `tools/`: Contains the tools and utilities that are used by the agents.
- `api/`: Contains the FastAPI application that provides the web interface and the REST API.
  - `ui/`: Contains the HTML, CSS, and JavaScript for the web interface.
- `docs/`: Contains high-level project documentation.

## 🤝 Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.