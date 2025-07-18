# **Technical Design Document: Agentic Code Sample Evaluator**

## **1\. Overview & System Architecture**

*A high-level diagram and description of the major components (UI, API, Agent(s)) and how they interact.*

The system follows a multi-agent architecture where the backend is stateless, but the frontend UI manages state within a user's session. The FastAPI backend serves as the API layer, orchestrating agents. The core logic resides in two ADK-based agents: an **Evaluation Agent** and a **Validation Agent**. The UI can make separate calls to evaluate code and then to validate the result of that evaluation.

**Architecture:**

\+--------------------------+                                 \+---------------------------------+  
|   UI (Vanilla JS, HTML)  |                                 |        API (FastAPI)            |  
| \- Stores last result     |                                 |                                 |  
\+--------------------------+                                 \+---------------------------------+  
           |         ^                                                 |                 ^  
 (1. POST /evaluate) | (2. Evaluation JSON)                  (Invoke Eval Agent) |  
           |         |                                                 |                 |  
           \+--------\>+------------------------------------------------\>+                 |  
                                                                       |                 |  
           |         ^                                                 v                 |  
 (3. POST /validate) | (4. Validation JSON)          \+---------------------------------+ |  
           |         |                               |      Evaluation Agent (ADK)     | |  
           \+--------\>+-----------------------------\> \+---------------------------------+ |  
                     (with code \+ eval JSON)           (Sends code \+ eval JSON)          |  
                                                                       |                 |  
                                                                       v                 |  
                                                       \+----------------------------------+  
                                                       |      Validation Agent (ADK)      |  
                                                       \+----------------------------------+

## **2\. Agent Design (ADK)**

*Detailed design of the agent(s).*

* **Overall Agent Strategy:** A **two-agent sequential pipeline** will be used. The first agent evaluates the code, and the second agent validates that evaluation. This separation of concerns allows for a more robust and reviewable process.  
* **Agent 1: Code Sample Evaluator**  
  * **Purpose:** To meticulously evaluate a given code sample based on a detailed set of criteria and produce a structured JSON response.  
  * **Tools:** Google Search. The agent's prompt will instruct it to prioritize search results from https://cloud.google.com and https://github.com/googleapis/googleapis to validate API correctness against the most current, official documentation.  
  * **Memory:** Stateless per request.  
  * **Output Schema:** A Pydantic model enforcing the strict JSON structure from the PRD.  
* **Agent 2: Evaluation Validation Agent**  
  * **Purpose:** To act as a critical reviewer of the Evaluation Agent's output. It will check for correctness, missed issues, and adherence to the original evaluation instructions.  
  * **Inputs:**  
    1. The original code sample.  
    2. The full JSON output from the Evaluation Agent.  
  * **Tools:** Google Search. The agent will use search to double-check API claims made by the first agent, again prioritizing official documentation sources like https://cloud.google.com and https://github.com/googleapis/googleapis.  
  * **Memory:** Stateless per request.  
  * **Output Schema:** A Pydantic model will be used to enforce the following output structure:  
    {  
      "is\_evaluation\_correct": "boolean",  
      "agreement\_score": "integer (0-100)",  
      "summary": "string (A concise summary of the validation findings.)",  
      "discrepancies": \[  
        {  
          "criterion\_name": "string",  
          "finding": "string (Description of the disagreement, e.g., 'The evaluation agent incorrectly flagged a valid API method.')"  
        }  
      \]  
    }

* **Language Handling Clarification:** For evaluation purposes, all common variants of JavaScript (e.g., TypeScript, Node.js, ECMAScript) will be categorized and treated as "JavaScript".

## **3\. API Design**

*Endpoint definitions, request/response schemas.*

* **Request Handling & Pre-processing:** The API layer orchestrates the entire workflow, including fetching code, pre-processing, and invoking the appropriate agent.  
* **Endpoints:**  
  1. **POST /evaluate**  
     * **Description:** Runs only the evaluation agent on a raw code string.  
     * **Request Body:**  
       {  
         "code": "string",  
         "language": "string (optional)",  
         "metadata": { "uri": "string (optional)" }  
       }

     * **Success Response:**  
       {  
         "request\_id": "string (UUID for tracking)",  
         "status": "completed",  
         "results": { /\* ... evaluation agent JSON output ... \*/ }  
       }

  2. **POST /evaluate-from-url**  
     * **Description:** Fetches code from a public GitHub URL and runs only the evaluation agent.  
     * **Request Body:**  
       {  
         "github\_url": "string"  
       }

     * **Success Response:** Same as /evaluate.  
  3. **POST /validate**  
     * **Description:** Runs only the validation agent on a code sample and its corresponding evaluation JSON.  
     * **Request Body:**  
       {  
         "code": "string",  
         "language": "string",  
         "evaluation\_results": { /\* ... evaluation agent JSON output from a previous run ... \*/ }  
       }

     * **Success Response:**  
       {  
         "request\_id": "string (UUID for tracking)",  
         "status": "completed",  
         "validation": { /\* ... validation agent JSON output ... \*/ }  
       }

## **4\. UI/UX Design**

*A brief on the user interface and user flow.*

The UI will manage the state of the last evaluation to allow for a two-step workflow.

* **User Flow:**  
  1. User provides code via paste or GitHub URL and clicks **"Evaluate"**.  
  2. The evaluation runs and the results are displayed in a "Results Card". The UI stores the original code and the full evaluation JSON in a client-side variable.  
  3. A new button, **"Validate this Result"**, is visible on the Results Card.  
  4. If the user clicks this button, the UI sends the stored code and evaluation JSON to the POST /validate endpoint.  
  5. The validation results are then displayed on the same Results Card.  
* **Key UI Components:**  
  * **Input Card:** Contains the text area, language selector, and "Evaluate" button. The "Validate" checkbox is removed.  
  * **Results Card:**  
    * Displays evaluation results.  
    * Contains a **"Validate this Result"** button, which is visible after an evaluation is complete.  
    * Has a section for **"Validation Feedback"** that is populated after the validation call.

## **5\. Technology Stack**

*List of technologies, frameworks, and services to be used.*

* **Agent Framework:** Google ADK (Python SDK)  
* **Backend:** Python 3.11+, FastAPI, httpx  
* **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+)  
* **Deployment:** Containerized and deployed to Google Cloud Run.

## **6\. Data Model & Persistence**

*How data will be stored (if at all).*

The application backend is **stateless**. No evaluation results or user data will be stored or persisted on the server between requests. However, the frontend UI will manage state for the duration of a browser session, temporarily storing the results of the last evaluation in memory to allow for subsequent validation.

## **7\. Risks & Mitigation**

*Potential technical challenges and how to address them.*

* **Risk:** The single-agent prompt becomes too complex, leading to degraded performance or accuracy.  
  * **Mitigation:** Start with a well-structured prompt. If issues arise, refactor into a multi-agent system.  
* **Risk:** The agent hallucinates or provides incorrect API validation.  
  * **Mitigation:** The prompt design emphasizes using search to verify. The two-agent design acts as a primary mitigation, allowing one agent to check the other's work.  
* **Risk:** Increased latency and cost from the two-agent pipeline.  
  * **Mitigation:** The workflow is now split into two distinct user actions, improving perceived performance. The user can choose not to run validation to manage cost.  
* **Risk:** The Validation Agent is not critical enough and simply agrees with the Evaluation Agent.  
  * **Mitigation:** The prompt for the Validation Agent must be carefully crafted to be adversarial. It should be instructed to be skeptical and to actively look for errors and missed opportunities in the initial evaluation.