# Backlog

* [x] **High: Security** - Secure the GitHub fetching endpoint to prevent SSRF vulnerabilities.
* [x] **High: Core Functionality** - Implement dynamic language detection in the API.
* [x] **High: Reliability** - Improve LLM JSON parsing by using function calling/tool use instead of regex.
* [x] **High: Reliability** - Enhance error handling in `ResultProcessingAgent`.
* [-] **Medium: Dependencies** - Centralize dependency management into a single `pyproject.toml` file.
* [ ] **Medium: Testing** - Implement a comprehensive test suite for the API and core orchestration logic.
* [ ] **Medium: Refactoring** - Consolidate the redundant `ProductCategorizationAgent` and `ProductIdentificationAgent`.
* [ ] **Medium: Configuration** - Centralize configuration by removing hardcoded model names.
* [ ] **Low: Refactoring** - Decouple the `remove_comments` function into a shared utility module.
* [ ] **Low: Project Structure** - Remove the redundant `agentic_code_analyzer/main.py` file.
* [ ] **Low: API** - Add input validation to the API endpoints.
* [ ] **Low: Prompts** - Enhance the specificity of prompts for the code analysis agents.
