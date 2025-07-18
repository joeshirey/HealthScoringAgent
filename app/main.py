import os
import uuid
import json
import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from agents.evaluation_agent import evaluation_agent, Evaluation
from agents.validation_agent import validation_agent, Validation


# ---------------- Pydantic Models ----------------

class EvaluateRequest(BaseModel):
    code: str
    language: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class EvaluateFromUrlRequest(BaseModel):
    github_url: str

class ValidateRequest(BaseModel):
    code: str
    language: str
    evaluation_results: Evaluation

class EvaluateResponse(BaseModel):
    request_id: str
    status: str = "completed"
    results: Evaluation

class ValidateResponse(BaseModel):
    request_id: str
    status: str = "completed"
    validation: Validation

# ---------------- FastAPI App ----------------

app = FastAPI(
    title="Agentic Code Sample Evaluator",
    description="An API for evaluating code samples using an agentic pipeline.",
    version="1.0.0"
)

# ---------------- Agent Initialization ----------------

evaluation_runner = InMemoryRunner(app_name="eval_runner", agent=evaluation_agent)
validation_runner = InMemoryRunner(app_name="validation_runner", agent=validation_agent)

# ---------------- API Endpoints ----------------

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to ensure the service is running.
    """
    return {"status": "ok"}

@app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_code(request: EvaluateRequest):
    """
    Runs the evaluation on a raw code string.
    """
    request_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    try:
        await evaluation_runner.session_service.create_session(
            app_name="eval_runner", user_id="user", session_id=session_id
        )
        response_text = ""
        prompt = f"""
Your task is to evaluate the following code:
{request.code}

Your response must be a structured JSON response that adheres to the following schema:
{json.dumps(Evaluation.model_json_schema(), indent=2)}
"""
        print(f"--- EVALUATION PROMPT ---\n{prompt}")
        async for event in evaluation_runner.run_async(
            user_id="user",
            session_id=session_id,
            state_delta={"LANGUAGE": request.language},
            new_message=Content(parts=[Part(text=prompt)]),
        ):
            if event.is_final_response():
                response_text = "".join(
                    part.text for part in event.content.parts
                )
        print(f"--- EVALUATION RESPONSE ---\n{response_text}")
        # Extract JSON from markdown code block
        json_text = response_text.split("```json")[1].split("```")[0]
        evaluation_result = Evaluation.model_validate_json(json_text)
        return EvaluateResponse(request_id=request_id, results=evaluation_result)
    except Exception as e:
        logging.exception("Error during code evaluation")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate-from-url", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_from_url(request: EvaluateFromUrlRequest):
    """
    Fetches code from a public GitHub URL and runs the evaluation.
    """
    request_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    try:
        await evaluation_runner.session_service.create_session(
            app_name="eval_runner", user_id="user", session_id=session_id
        )
        
        raw_url = request.github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        language = "unknown"
        if "." in raw_url:
            extension = raw_url.split(".")[-1]
            lang_map = {
                "py": "Python", "js": "JavaScript", "ts": "TypeScript",
                "java": "Java", "go": "Go", "rb": "Ruby", "php": "PHP",
                "cs": "C#", "cpp": "C++", "c": "C", "html": "HTML",
                "css": "CSS", "sh": "Shell",
            }
            language = lang_map.get(extension, "unknown")

        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            code = response.text

        response_text = ""
        prompt = f"""
Your task is to evaluate the following code:
{code}

Your response must be a structured JSON response that adheres to the following schema:
{json.dumps(Evaluation.model_json_schema(), indent=2)}
"""
        print(f"--- EVALUATION PROMPT ---\n{prompt}")
        async for event in evaluation_runner.run_async(
            user_id="user",
            session_id=session_id,
            state_delta={"LANGUAGE": language},
            new_message=Content(parts=[Part(text=prompt)]),
        ):
            if event.is_final_response():
                response_text = "".join(
                    part.text for part in event.content.parts
                )
        print(f"--- EVALUATION RESPONSE ---\n{response_text}")
        # Extract JSON from markdown code block
        json_text = response_text.split("```json")[1].split("```")[0]
        evaluation_result = Evaluation.model_validate_json(json_text)
        return EvaluateResponse(request_id=request_id, results=evaluation_result)
    except httpx.HTTPStatusError as e:
        logging.exception("Failed to fetch code from URL")
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch code from URL.")
    except Exception as e:
        logging.exception("Error during evaluation from URL")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate", response_model=ValidateResponse, tags=["Validation"])
async def validate_evaluation(request: ValidateRequest):
    """
    Runs the validation on a code sample and its corresponding evaluation.
    """
    request_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    try:
        await validation_runner.session_service.create_session(
            app_name="validation_runner", user_id="user", session_id=session_id
        )
        response_text = ""
        prompt = f"""
Your task is to validate the following evaluation for the provided {request.language} code.

Code:
{request.code}

Evaluation:
{request.evaluation_results.dict()}

Your response must be a structured JSON response that adheres to the following schema:
{json.dumps(Validation.model_json_schema(), indent=2)}
"""
        print(f"--- VALIDATION PROMPT ---\n{prompt}")
        async for event in validation_runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=Content(parts=[Part(text=prompt)]),
        ):
            if event.is_final_response():
                response_text = "".join(
                    part.text for part in event.content.parts
                )
        print(f"--- VALIDATION RESPONSE ---\n{response_text}")
        # Extract JSON from markdown code block
        json_text = response_text.split("```json")[1].split("```")[0]
        validation_result = Validation.model_validate_json(json_text)
        return ValidateResponse(request_id=request_id, validation=validation_result)
    except Exception as e:
        logging.exception("Error during validation")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Static Files ----------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
