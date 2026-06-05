import os
import json
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

system_prompt = "You are a helpful assistant that breaks down problems into steps and solves them systematically."

  

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