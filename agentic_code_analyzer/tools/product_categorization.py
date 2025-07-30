"""
This module provides the logic for categorizing a code sample into a specific
product and product category. It uses a hybrid approach, combining a fast,
rule-based method with a more powerful but slower LLM fallback.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import yaml
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def _load_product_config() -> Tuple[
    Dict[Tuple[str, str], List[str]], List[Tuple[str, str]]
]:
    """
    Loads and merges product hierarchy and keywords from the YAML config.

    This function reads the `product_hierarchy.yaml` file, which defines the
    categories, products, and associated keywords. It also defines a static
    ordered list of products to ensure a consistent search order, prioritizing
    more specific products over general ones.

    Returns:
        A tuple containing:
        - A dictionary mapping (category, product) tuples to a list of keywords.
        - A list of (category, product) tuples in a predefined search order.
    """
    hierarchy: Dict[Tuple[str, str], List[str]] = {}
    # This list defines the search order to prevent miscategorization.
    # For example, "BigQuery Migration" should be checked before "BigQuery".
    ordered_products: List[Tuple[str, str]] = [
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

    # Load all products from the YAML file and add them to the hierarchy.
    all_products_from_yaml: List[Tuple[str, str]] = []
    for category_info in product_config:
        category_name = category_info["category"]
        for product_info in category_info["products"]:
            product_name = product_info["product"]
            key = (category_name, product_name)
            hierarchy[key] = product_info.get("keywords", [])
            all_products_from_yaml.append(key)

    # Ensure all products from the YAML are in the ordered list.
    for product in all_products_from_yaml:
        if product not in ordered_products:
            ordered_products.append(product)

    return hierarchy, ordered_products


# Load the product configuration at module import time.
PRODUCT_HIERARCHY, ORDERED_PRODUCTS = _load_product_config()


def _find_product_by_rules(
    search_string: Optional[str],
) -> Optional[Tuple[str, str]]:
    """
    Finds a product by matching keywords against a search string.

    This function iterates through the `ORDERED_PRODUCTS` list and uses regex
    to search for associated keywords in the provided string (e.g., a GitHub
    link or region tag).

    Args:
        search_string: The string to search for keywords.

    Returns:
        A tuple of (category, product) if a match is found, otherwise None.
    """
    if not isinstance(search_string, str):
        return None

    search_string_lower = search_string.lower()
    for category, product in ORDERED_PRODUCTS:
        keywords = PRODUCT_HIERARCHY.get((category, product), [])
        for keyword in keywords:
            try:
                # Use regex for flexible matching.
                if re.search(keyword, search_string_lower):
                    return category, product
            except re.error:
                # Fallback to simple string containment if regex is invalid.
                if keyword in search_string_lower:
                    return category, product
    return None


def _categorize_with_llm(
    code_content: str, product_list: List[Tuple[str, str]]
) -> Tuple[str, str]:
    """
    Analyzes code content using an LLM for categorization.

    This function sends the code snippet to a large language model and asks it
    to choose the most appropriate product from a provided list. This is used
    as a fallback when rule-based methods fail.

    Args:
        code_content: The code snippet to analyze.
        product_list: The list of valid (category, product) tuples.

    Returns:
        A tuple of (category, product) as determined by the LLM. Returns
        ("Uncategorized", "Uncategorized") on failure.
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
            temperature=0.0,  # Set to 0 for deterministic output.
            top_p=0.9,
        )

        response = client.models.generate_content(
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
            contents=prompt,
            config=generation_config,
        )

        # Extract the JSON from the response, even if it's in a markdown block.
        text_to_load = response.text.strip() if response.text else ""
        logger.info(f"LLM response for categorization: '{text_to_load}'")
        match = re.search(r"```json\s*({.*?})\s*```", text_to_load, re.DOTALL)
        if match:
            text_to_load = match.group(1)

        result = json.loads(text_to_load)
        category = result.get("category", "Uncategorized")
        product = result.get("product", "Uncategorized")

        return category, product

    except (json.JSONDecodeError, AttributeError, Exception) as e:
        logger.error(f"LLM categorization failed: {e}", exc_info=True)
        return "Uncategorized", "Uncategorized"


def categorize_sample(
    code_content: str = "",
    github_link: Optional[str] = None,
    region_tag: Optional[str] = None,
    llm_fallback: bool = False,
) -> Tuple[str, str, bool]:
    """
    Categorizes a code sample using a multi-stage, rule-based process with an
    optional LLM fallback.

    The process is as follows:
    1.  Check the `github_link` for keywords.
    2.  If no match, check the `region_tag` for keywords.
    3.  If still no match and `llm_fallback` is True, use the LLM to analyze
        the `code_content`.

    Args:
        code_content: The full code snippet.
        github_link: The GitHub URL of the code sample.
        region_tag: The region tag associated with the code.
        llm_fallback: Whether to use the LLM if rule-based methods fail.

    Returns:
        A tuple containing:
        - The determined product category.
        - The determined product name.
        - A boolean indicating if the LLM was used.
    """
    # Prioritize rule-based matching on the GitHub link for accuracy.
    if github_link:
        result = _find_product_by_rules(github_link)
        if result:
            return result[0], result[1], False

    # Use the region tag as a secondary source for rule-based matching.
    if region_tag:
        result = _find_product_by_rules(region_tag)
        if result:
            return result[0], result[1], False

    # As a last resort, use the LLM if enabled.
    if llm_fallback and code_content:
        llm_result = _categorize_with_llm(code_content, ORDERED_PRODUCTS)
        if llm_result[0] != "Uncategorized":
            return llm_result[0], llm_result[1], True

    # If all methods fail, return "Uncategorized".
    return "Uncategorized", "Uncategorized", False
