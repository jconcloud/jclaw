import subprocess
import urllib.request

from bs4 import BeautifulSoup

def http_fetch(url: str, max_chars: int = 5000) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "my-agent/0.1"})
    with urllib.request.urlopen(req, timeout=10) as r:
        ct = r.headers.get("Content-Type", "")
        body = r.read(200_000).decode("utf-8", errors="replace")
    if "html" in ct:
        soup = BeautifulSoup(body, "html.parser")
        # Drop non-content tags so they don't pollute the extracted text.
        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()
        body = " ".join(soup.get_text(separator=" ").split())
    return body[:max_chars]

def calculator(expression):
    """
    Evaluate mathematical expressions.
    WARNING: This tutorial uses eval() for simplicity but it is not recommended for production use.

    Args:
        expression (str): The mathematical expression to evaluate
    Returns:
        float: The result of the evaluation
    """
    try:
        result = eval(expression)
        return {"result": result}
    except Exception:
        return {"error": "Invalid mathematical expression"}
    
def run_python(code: str) -> str:
    """
    Executes python code and returns the output.

    Args:
        code (str): the python code to execute
    Returns:
        str: The result of the execution
    """
    try:
        out = subprocess.run(
            ["python3", "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout + out.stderr
    except Exception as e:
        return f"Error: {e}"


TOOLS = {
    "calculator": {
        "fn": calculator,
        "schema": {
            "name": "calculator",
            "description": "Performs basic mathematical calculations, use also for simple additions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            }
        },
    },
    "run_python": {
        "fn": run_python,
        "schema": {
            "name": "run_python",
            "description": "Execute Python code and return stdout/stderr.",
            "input_schema": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"],
            },
        },
    },
    "http_fetch": {
        "fn": http_fetch,
        "schema": {
            "name": "http_fetch",
            "description": "Fetch the text content of a web page given its URL.",
            "input_schema": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    # Anthropic server-side tool: the API runs the search itself, so there is
    # no local fn. The schema uses the {type, name} shape (not input_schema),
    # and the model's results come back as server_tool_use / web_search_tool_result
    # blocks that the agent loop ignores (it only executes block.type == "tool_use").
    "web_search": {
        "fn": None,
        "schema": {
            "type": "web_search_20260209",
            "name": "web_search",
            # "max_uses": 5,  # optional: cap searches per request to bound cost
        },
    },
}
  