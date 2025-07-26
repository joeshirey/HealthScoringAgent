# Product Requirements Document: Health Scoring Agent

## 1. Introduction

The Health Scoring Agent is a multi-agent system designed to automate the analysis and evaluation of code samples. The system provides a comprehensive and nuanced assessment of code health, including quality, correctness, and adherence to best practices. This document outlines the product requirements for the Health Scoring Agent.

## 2. Goals

The primary goals of the Health Scoring Agent are to:

*   **Automate code analysis:** Reduce the time and effort required to evaluate code samples.
*   **Improve code quality:** Provide developers with actionable feedback to improve their code.
*   **Ensure consistency:** Standardize the criteria and process for evaluating code.
*   **Provide a comprehensive assessment:** Evaluate code against a wide range of criteria, including quality, correctness, and best practices.

## 3. Functional Requirements

### 3.1. Code Analysis

The system shall be able to analyze code samples written in a variety of languages, including:

*   Python
*   Java
*   JavaScript
*   Go
*   C#
*   Ruby
*   PHP
*   Terraform
*   Rust
*   C++

The system shall evaluate code against the following criteria:

*   **Runnability and Configuration:** The code should be runnable by default, with minimal configuration.
*   **API Effectiveness and Correctness:** The code should use APIs correctly and effectively.
*   **Comments and Code Clarity:** The code should be well-commented and easy to understand.
*   **Formatting and Consistency:** The code should be well-formatted and consistent with the canonical style guide for the language.
*   **Language Best Practices:** The code should follow idiomatic constructs and avoid anti-patterns.
*   **LLM Training Fitness and Explicitness:** The code should be explicit, self-documenting, and suitable for training large language models.

### 3.2. Product Categorization

The system shall be able to categorize code samples into a specific Google Cloud product. The categorization shall be based on a combination of rules-based logic and a large language model.

### 3.3. Output

The system shall produce a structured JSON object that contains the results of the analysis. The JSON object shall include the following information:

*   **Overall Compliance Score:** A score from 0 to 100 that represents the overall health of the code.
*   **Criteria Breakdown:** A detailed breakdown of the score for each evaluation criterion.
*   **Recommendations:** A list of actionable recommendations for improving the code.
*   **Citations:** A list of citations that support the analysis.
*   **Language:** The programming language of the code sample.
*   **Product Name:** The name of the Google Cloud product that the code sample is for.
*   **Product Category:** The category of the Google Cloud product that the code sample is for.
*   **Region Tags:** A list of the region tags that were extracted from the code sample.

## 4. Non-Functional Requirements

### 4.1. Performance

The system shall be able to analyze a code sample in a timely manner. The target analysis time is less than 60 seconds per file.

### 4.2. Scalability

The system shall be able to scale to handle a large number of code samples. The system shall be able to analyze at least 1,000 files per day.

### 4.3. Reliability

The system shall be reliable and produce consistent results. The system shall have an uptime of at least 99.9%.

### 4.4. Extensibility

The system shall be extensible and easy to maintain. It shall be easy to add support for new languages, new evaluation criteria, and new output formats.

### 4.5. Security

The system shall be secure and protect the confidentiality and integrity of the code samples that it analyzes. The system shall not store any code samples after the analysis is complete.