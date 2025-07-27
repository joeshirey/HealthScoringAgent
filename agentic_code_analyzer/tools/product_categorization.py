import re
import os
import yaml
import json
from typing import Optional
from google import genai
from google.genai import types


def _load_product_config():
    """
    Loads and merges product hierarchy and keywords from the YAML configuration.
    """
    hierarchy = {}
    ordered_products = [
        ("Data Analytics", "BigQuery Migration"),
        ("Data Analytics", "BigQuery Data Transfer"),
        ("Data Analytics", "BigQuery Reservation"),
        ("Data Analytics", "BigQuery Connection"),
        ("Databases", "Cloud SQL"),
        ("Storage", "Storage Transfer Service"),
        ("Storage", "Storage Insights"),
        ("Storage", "Storage Control"),
        ("AI and Machine Learning", "Vertex AI Search"),
    ]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, "product_hierarchy.yaml")

    with open(yaml_path, "r") as f:
        product_config = yaml.safe_load(f)

    all_products_from_yaml = []
    for category_info in product_config:
        category_name = category_info["category"]
        for product_info in category_info["products"]:
            product_name = product_info["product"]
            key = (category_name, product_name)
            hierarchy[key] = product_info.get("keywords", [])
            all_products_from_yaml.append(key)

    for product in all_products_from_yaml:
        if product not in ordered_products:
            ordered_products.append(product)

    return hierarchy, ordered_products


PRODUCT_HIERARCHY, ORDERED_PRODUCTS = _load_product_config()


def _find_product_by_rules(search_string: Optional[str]) -> Optional[tuple[str, str]]:
    """
    Finds a product by matching keywords against a search string.
    """
    if not isinstance(search_string, str):
        return None

    search_string_lower = search_string.lower()
    for category, product in ORDERED_PRODUCTS:
        keywords = PRODUCT_HIERARCHY.get((category, product), [])
        for keyword in keywords:
            try:
                if re.search(keyword, search_string_lower):
                    return category, product
            except re.error:
                if keyword in search_string_lower:
                    return category, product
    return None


def _categorize_with_llm(code_content: str, product_list: list) -> tuple[str, str]:
    """
    Analyzes code content using a large language model (LLM) for categorization.
    """
    try:
        client = genai.Client()
        formatted_product_list = "\n".join(
            [f"- Category: {cat}, Product: {prod}" for cat, prod in product_list]
        )

        prompt = f"""
        You are an expert Google Cloud developer. Your task is to categorize a code sample into a specific Google Cloud product.
        Analyze the following code, paying close attention to import statements, client library initializations, and API calls.

        Code Sample:
        ```
        {code_content[:15000]}
        ```

        Based on your analysis, choose the single best-fitting product from the following list:
        {formatted_product_list}

        Return your answer as a single, valid JSON object with two keys: "category" and "product". Do not include any other text or formatting.
        Example: {{"category": "Databases", "product": "Spanner"}}
        """

        generation_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
        )

        response = client.models.generate_content(
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
            contents=prompt,
            config=generation_config,
        )

        text_to_load = response.text.strip() if response.text else ""
        match = re.search(r"```json\s*({.*?})\s*```", text_to_load, re.DOTALL)
        if match:
            text_to_load = match.group(1)

        result = json.loads(text_to_load)
        category = result.get("category", "Uncategorized")
        product = result.get("product", "Uncategorized")

        return category, product

    except (json.JSONDecodeError, AttributeError, Exception):
        return "Uncategorized", "Uncategorized"


def categorize_sample(
    code_content: str = "",
    github_link: Optional[str] = None,
    region_tag: Optional[str] = None,
    llm_fallback: bool = False,
) -> tuple[str, str, bool]:
    """
    Categorizes a code sample using a two-stage process.
    """
    if github_link:
        result = _find_product_by_rules(github_link)
        if result:
            return result[0], result[1], False

    if region_tag:
        result = _find_product_by_rules(region_tag)
        if result:
            return result[0], result[1], False

    if llm_fallback and code_content:
        llm_result = _categorize_with_llm(code_content, ORDERED_PRODUCTS)
        if llm_result[0] != "Uncategorized":
            return llm_result[0], llm_result[1], True

    return "Uncategorized", "Uncategorized", False
