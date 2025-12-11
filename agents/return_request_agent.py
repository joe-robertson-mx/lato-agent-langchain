from typing import Any, Dict
import json
import requests
from langchain.agents import create_agent


# System and User prompt templates for the return request agent
SYSTEM_PROMPT = (
    "Role: You are an AI assistant for a customer service representative (CSR) at an e-bike manufacturer. "
    "Your job is to organize customer repair issues into a clear, actionable plan for the CSR.\n\n"
    "Core Task: Your task is to receive a customer's problem description, identify the key details needed for a repair, "
    "and research useful information from various Lato systems and provide that to the CSR. You should consider the customers "
    "order history, value of the part and cost of repair when proposing your plan.\n\n"
    "Final Output: Your response must be a structured summary using the following format.\n\n"
    "Repair Request Summary\n"
    "Customer: [Customer's full name and company]\n"
    "Part: [Name and serial number (if provided)]\n"
    "Problem: [A detailed description of the issue]\n"
    "Next Steps: [A clear, simple action plan for the CSR]"
)

USER_PROMPT_TEMPLATE = "From: {{From}}\nContent: {{InputContent}}"


def get_customer_order_data(email: str) -> Any:
    """Retrieve customer order data for a given email.

    Returns the parsed JSON response from the order management REST endpoint.
    """
    url = "https://midaas-accp.mendixcloud.com/rest/ordermanagement/v1/order"
    params = {"email": email}
    headers = {"Accept": "application/json"}
    timeout = (3.05, 15)  # (connect_timeout, read_timeout)

    with requests.Session() as session:
        resp = session.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        # Try to parse JSON; if the response body is empty or not JSON, return useful debug info
        try:
            return resp.json()
        except ValueError:
            # JSON decoding failed — include status code and a snippet of the body for debugging
            text = resp.text or ""
            snippet = text[:1000]
            return {
                "_error": "invalid_json_response",
                "status_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type"),
                "text_snippet": snippet,
            }


def format_user_prompt(from_field: str, input_content: str) -> str:
    """Fill the user prompt template with the provided values."""
    return USER_PROMPT_TEMPLATE.replace("{{From}}", from_field).replace("{{InputContent}}", input_content)


def create_return_request_agent(model: str = "openai:gpt-5-mini"):
    """Create the return request agent preconfigured with tools and system prompt.

    Note: `create_agent` may require additional optional dependencies (e.g., `langgraph`).
    """
    agent = create_agent(
        model=model,
        tools=[get_customer_order_data],
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


def run_return_request_agent(
    from_field: str, input_content: str, model: str = "openai:gpt-5-mini"
) -> Dict[str, Any]:
    """Create and invoke the return request agent using a formatted user prompt.

    Returns a tuple `(raw_result, summary_text)` where `summary_text` is the
    textual Repair Request Summary extracted from the agent output (or None).
    """
    user_prompt = format_user_prompt(from_field, input_content)
    agent = create_return_request_agent(model=model)
    raw_result = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})

    # Try to extract the human-readable repair summary from the run
    summary_text = None
    try:
        # Lazy import of helper to avoid extra deps if unused
        from utils.print_helpers import find_repair_summary

        summary_text = find_repair_summary(raw_result)
    except Exception:
        summary_text = None

    return {"raw": raw_result, "summary": summary_text}



