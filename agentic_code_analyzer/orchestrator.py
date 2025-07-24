import json
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
from agentic_code_analyzer.agents.language_detection_agent import LanguageDetectionAgent
from agentic_code_analyzer.agents.region_tag_agent import RegionTagExtractionAgent
from agentic_code_analyzer.agents.product_id_agent import ProductIdentificationAgent
from agentic_code_analyzer.agents.analysis.code_quality_agent import CodeQualityAgent
from agentic_code_analyzer.agents.analysis.api_analysis_agent import ApiAnalysisAgent
from agentic_code_analyzer.agents.analysis.clarity_readability_agent import ClarityReadabilityAgent
from agentic_code_analyzer.agents.analysis.runnability_agent import RunnabilityAgent
from agentic_code_analyzer.evaluation_agent.evaluation_agent import EvaluationReviewAgent

class CodeAnalyzerOrchestrator(BaseAgent):
    """A custom agent that orchestrates the code analysis workflow."""

    language_detection_agent: LlmAgent
    region_tag_extraction_agent: LlmAgent
    product_identification_agent: LlmAgent
    code_quality_agent: LlmAgent
    api_analysis_agent: LlmAgent
    clarity_readability_agent: LlmAgent
    runnability_agent: LlmAgent
    evaluation_review_agent: LlmAgent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language_detection_agent = LanguageDetectionAgent(name="language_detection_agent", output_key="language_detection_agent_output")
        self.region_tag_extraction_agent = RegionTagExtractionAgent(name="region_tag_extraction_agent", output_key="region_tag_extraction_agent_output")
        self.product_identification_agent = ProductIdentificationAgent(name="product_identification_agent", output_key="product_identification_agent_output")
        self.code_quality_agent = CodeQualityAgent(name="code_quality_agent", output_key="code_quality_agent_output")
        self.api_analysis_agent = ApiAnalysisAgent(name="api_analysis_agent", output_key="api_analysis_agent_output")
        self.clarity_readability_agent = ClarityReadabilityAgent(name="clarity_readability_agent", output_key="clarity_readability_agent_output")
        self.runnability_agent = RunnabilityAgent(name="runnability_agent", output_key="runnability_agent_output")
        self.evaluation_review_agent = EvaluationReviewAgent(name="evaluation_review_agent", output_key="evaluation_review_agent_output")

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        code_snippet = ctx.session.state["code_snippet"]

        # 1. Language Detection
        async for event in self.language_detection_agent.run_async(ctx):
            yield event
        language = ctx.session.state["language_detection_agent_output"]

        # 2. Region Tag Extraction
        async for event in self.region_tag_extraction_agent.run_async(ctx):
            yield event
        region_tags = ctx.session.state["region_tag_extraction_agent_output"]

        # 3. Product Identification
        async for event in self.product_identification_agent.run_async(ctx):
            yield event
        product_info = ctx.session.state["product_identification_agent_output"]
        product_name, product_category = product_info.split(",")

        # 4. Code Analysis
        async for event in self.code_quality_agent.run_async(ctx):
            yield event
        code_quality_assessment = ctx.session.state["code_quality_agent_output"]

        async for event in self.api_analysis_agent.run_async(ctx):
            yield event
        api_analysis_assessment = ctx.session.state["api_analysis_agent_output"]

        async for event in self.clarity_readability_agent.run_async(ctx):
            yield event
        clarity_and_readability_assessment = ctx.session.state["clarity_readability_agent_output"]

        async for event in self.runnability_agent.run_async(ctx):
            yield event
        runnability_assessment = ctx.session.state["runnability_agent_output"]

        # 5. Structured Output Generation
        analysis_output = {
            "language": language,
            "product_name": product_name.strip(),
            "product_category": product_category.strip(),
            "region_tags": region_tags.split(","),
            "analysis": {
                "quality_summary": code_quality_assessment,
                "api_usage_summary": api_analysis_assessment,
                "best_practices_summary": clarity_and_readability_assessment,
            },
        }
        ctx.session.state["analysis_output"] = analysis_output

        # 6. Evaluation Review
        async for event in self.evaluation_review_agent.run_async(ctx):
            yield event
        evaluation = ctx.session.state["evaluation_review_agent_output"]
        analysis_output["evaluation"] = evaluation

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=json.dumps(analysis_output))]),
            turn_complete=True,
        )
