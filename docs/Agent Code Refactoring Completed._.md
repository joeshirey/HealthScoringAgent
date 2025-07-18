# **Product Requirements Document: Agentic Code Sample Evaluator**

## **1\. Introduction & Problem Statement**

Evaluating code samples for technical documentation is a manual, time-consuming, and often inconsistent process. Developers and technical writers need a tool that can rapidly and accurately assess a code sample's quality against a set of objective standards. This ensures that all published code is correct, clear, idiomatic, and follows best practices.

**Problem:** The process of reviewing code samples is slow, subjective, and prone to human error, leading to inconsistent quality in documentation.

**Vision:** To create an intelligent, agent-based application that fully automates the evaluation of code samples, providing developers with instant, structured, and actionable feedback to improve documentation quality and accelerate the content lifecycle.

## **2\. User Personas**

* **Primary User: Technical Writer / Content Creator**  
  * **Needs:** Needs a fast, reliable way to verify that a code sample received from a developer is correct and adheres to style guidelines. They may not be a deep expert in the specific programming language and require clear, easy-to-understand feedback on what needs to be fixed.  
* **Secondary User: Software Developer**  
  * **Needs:** Needs a quick "linting" tool to check if their code sample meets all documentation standards before submitting it to the technical writing team. This saves them time and reduces back-and-forth communication.  
* **Implicit User: LLM Fine-Tuning Process**  
  * **Needs:** The structured JSON output serves as a high-quality, clean dataset. This data can be used to train future language models to automatically correct or generate documentation-quality code samples.

## **3\. Features & Scope**

### **3.1. Core Feature: Code Evaluation**

The system will accept a code snippet and evaluate it against a comprehensive set of criteria.

* **Inputs:** Raw code string, an optional programming language, and optional metadata (like a URI).  
* **Criteria:** The evaluation is based on the following weighted criteria:  
  1. **Runnability & Configuration (15%)**: Checks for runnable structure and proper use of environment variables.  
  2. **API Effectiveness & Correctness (40%)**: Validates client libraries, methods, and parameters against official documentation. This is the most critical check.  
  3. **Comments & Code Clarity (10%)**: Assesses the readability and quality of comments and code.  
  4. **Formatting & Consistency (10%)**: Checks for adherence to language-specific style guides (e.g., PEP 8).  
  5. **Language Best Practices (15%)**: Ensures the use of idiomatic code and modern, non-deprecated features.  
  6. **LLM Training Fitness (10%)**: Evaluates if the code is explicit and unambiguous, making it a good learning example.  
* **Output:** The system will produce a single, strictly-validated JSON object containing:  
  * An overall compliance score.  
  * A breakdown of scores and weights for each criterion.  
  * A detailed text assessment for each criterion.  
  * A list of specific, actionable recommendations an LLM can use to fix the code.

### **3.2. Feature: GCP Product Identification**

The system will analyze the code's URI, region tags, and content to automatically identify the primary Google Cloud Platform product and product category being demonstrated.

### **3.3. Feature: Evaluation Validation**

A second, independent agent acts as a reviewer to ensure the quality and accuracy of the initial evaluation.

* The user can trigger this validation agent on a completed evaluation.  
* The agent will provide an agreement score and a summary of any discrepancies found, providing a "second opinion" on the evaluation's correctness.

### **3.4. Feature: Input Flexibility**

* Users can paste raw code directly into the UI.  
* Users can provide a public GitHub URL to a code file, which the system will automatically fetch.  
* The system will attempt to infer the programming language from the code snippet if it is not explicitly provided.

## **4\. Non-Goals**

* **Full Code Execution Environment:** The system performs static analysis. It will not compile or run the code in a sandboxed environment.  
* **Cross-Sample Consistency:** Evaluation is performed on a per-sample basis. The system will not check for consistency across an entire repository of samples.  
* **User Authentication:** The application will be public and will not have user accounts or login functionality.