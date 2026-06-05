import subprocess

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
}
  