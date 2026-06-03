import os
import json
import asyncio
import subprocess
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

system_prompt = "You are a helpful assistant that breaks down problems into steps and solves them systematically."

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
    

async def agent(prompt: str, max_turns: int = 5) -> None:
    messages = [{"role": "user", "content": prompt}]
    tool_schemas = [t["schema"] for t in TOOLS.values()]

    for turn in range(max_turns):
        print(f"\n=== Turn {turn + 1}/{max_turns} ===")
        async with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            output_config={"effort": "low"},
            system=system_prompt,
            messages=messages,
            tools=tool_schemas,
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)
            print()  # newline after streamed text

            message = await stream.get_final_message()  # full reconstructed message
        
        
        stop_reason = message.stop_reason
        print(f"=== Stop reason: {stop_reason} ===")
        if stop_reason != "tool_use":
            break

        tool_results = []
        for block in message.content:
            if block.type == "tool_use":
                print(f"=== Using tool {block.name} with input {block.input} ===")
                fn = TOOLS[block.name]["fn"]
                result = fn(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
        messages.append({"role": "assistant", "content": message.content})  # add messages to the short memory context
        messages.append({"role": "user", "content": tool_results})



prompt = "I had 12 apples, and I lost a third. Then a friend gave me 2. How many apples do I have?"
max_turns = 3
asyncio.run(agent(prompt, max_turns))