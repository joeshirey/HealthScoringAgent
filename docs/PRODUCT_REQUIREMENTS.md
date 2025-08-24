# Product Requirements Document: Health Scoring Agent

## 1. Introduction

The Health Scoring Agent is a multi-agent system designed to automate the analysis and evaluation of code samples. The system provides a comprehensive and nuanced assessment of code health, including quality, correctness, and adherence to best practices. This document outlines the product requirements for the Health Scoring Agent.

## 2. Goals

The primary goals of the Health Scoring Agent are to:

- **Automate code analysis:** Reduce the time and effort required to evaluate code samples.
- **Improve code quality:** Provide developers with actionable feedback to improve their code.
- **Ensure consistency:** Standardize the criteria and process for evaluating code.
- **Provide a comprehensive assessment:** Evaluate code against a wide range of criteria, including quality, correctness, and best practices.

## 3. Functional Requirements

### 3.1. Code Analysis

The system is designed to be extensible for analyzing code samples in various programming languages. The initial implementation focuses on common languages such as Python, Java, C#, Go, and JavaScript.

The system shall evaluate code against the following core criteria:

- **Runnability and Configuration:** Assesses whether the code is runnable by default, with clear dependency management and secure configuration practices.
- **API Effectiveness and Correctness:** Evaluates the correct and effective use of APIs, including error handling, security, and best practices.
- **Code Quality:** Analyzes formatting, consistency, adherence to language best practices, naming conventions, and code complexity.
- **Clarity and Readability:** Assesses the clarity and readability of the code, including the use of comments and the overall structure of the code.

### 3.2. Product Categorization

The system shall be able to categorize code samples into a specific Google Cloud product. The categorization shall be based on a combination of rules-based logic and a large language model.

### 3.3. Advanced Prompting

The system shall leverage advanced prompt engineering techniques to guide the Large Language Models (LLMs). This includes:

- **Persona-driven Prompts:** Assigning specific, expert personas to the LLM for each analysis task (e.g., "Senior DevOps Engineer," "Principal Engineer").
- **Structured Instructions:** Providing clear, detailed instructions and checklists for the analysis.
- **Schema Enforcement:** Defining a strict JSON schema for the output to ensure consistency and reliability.

### 3.4. Output

The system shall produce a structured JSON object that contains the results of the analysis. The JSON object shall include the following information:

- **Overall Compliance Score:** A score from 0 to 100 that represents the overall health of the code.
- **Criteria Breakdown:** A detailed breakdown of the score for each evaluation criterion.
- **Recommendations:** A list of actionable recommendations for improving the code.
- **Citations:** A list of citations that support the analysis.
- **Language:** The programming language of the code sample.
- **Product Name:** The name of the Google Cloud product that the code sample is for.
- **Product Category:** The category of the Google Cloud product that the code sample is for.
- **Region Tags:** A list of the region tags that were extracted from the code sample.

## 4. Non-Functional Requirements

### 4.1. Performance

The system shall be able to analyze a code sample in a timely manner. The target analysis time is less than 60 seconds per file, but this may vary depending on the complexity of the code and the number of validation loops required.

### 4.2. Scalability

The system shall be able to scale to handle a large number of code samples. The system shall be able to analyze at least 1,000 files per day.

### 4.3. Reliability

The system shall be reliable and produce consistent results. The system shall have an uptime of at least 99.9%.

### 4.4. Extensibility

The system shall be extensible and easy to maintain. It shall be easy to add support for new languages, new evaluation criteria, and new output formats.

### 4.5. Security

The system shall be secure and protect the confidentiality and integrity of the code samples that it analyzes. The system shall not store any code samples after the analysis is complete.
