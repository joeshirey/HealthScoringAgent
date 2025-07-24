import asyncio
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
from agentic_code_analyzer.agents.language_detection_agent import LanguageDetectionAgent
from agentic_code_analyzer.agents.region_tag_agent import RegionTagExtractionAgent
from agentic_code_analyzer.agents.product_id_agent import ProductIdentificationAgent
from agentic_code_analyzer.agents.analysis.code_quality_agent import CodeQualityAgent
from agentic_code_analyzer.agents.analysis.api_analysis_agent import ApiAnalysisAgent
from agentic_code_analyzer.agents.analysis.clarity_readability_agent import ClarityReadabilityAgent
from agentic_code_analyzer.agents.analysis.runnability_agent import RunnabilityAgent
from agentic_code_analyzer.evaluation_agent.evaluation_agent import EvaluationReviewAgent

async def main():
    """Runs the agentic code analyzer."""
    code_snippet = '''
# [START vision_quickstart]
import io
import os

# Imports the Google Cloud client library
from google.cloud import vision

# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.abspath('resources/wakeupcat.jpg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)
# [END vision_quickstart]
'''
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="test_user",
        session_id="test_session",
        state={"code_snippet": code_snippet},
    )

    runner = Runner(
        agent=CodeAnalyzerOrchestrator(
            name="code_analyzer_orchestrator",
            language_detection_agent=LanguageDetectionAgent(name="language_detection_agent"),
            region_tag_extraction_agent=RegionTagExtractionAgent(name="region_tag_extraction_agent"),
            product_identification_agent=ProductIdentificationAgent(name="product_identification_agent"),
            code_quality_agent=CodeQualityAgent(name="code_quality_agent"),
            api_analysis_agent=ApiAnalysisAgent(name="api_analysis_agent"),
            clarity_readability_agent=ClarityReadabilityAgent(name="clarity_readability_agent"),
            runnability_agent=RunnabilityAgent(name="runnability_agent"),
            evaluation_review_agent=EvaluationReviewAgent(name="evaluation_review_agent"),
        ),
        app_name="agentic_code_analyzer",
        session_service=session_service,
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="test_user", session_id="test_session", new_message=types.Content(parts=[types.Part(text=code_snippet)])
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    print(json.dumps(json.loads(final_response), indent=4))

if __name__ == "__main__":
    asyncio.run(main())
