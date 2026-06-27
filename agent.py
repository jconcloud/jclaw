import os
import json

from anthropic import AsyncAnthropic, APIStatusError

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

system_prompt = "You are a helpful assistant that breaks down problems into steps and solves them systematically"
  
async def run_agent(prompt: str, tools: dict, max_turns: int = 5) -> None:
    messages = [{"role": "user", "content": prompt}]
    tool_schemas = [t["schema"] for t in tools.values()]
    container_id = None  # set once web_search's code-execution container is created

    for turn in range(max_turns):
        print(f"\n=== Iteration {turn + 1}/{max_turns} ===")
        request_kwargs = dict(
            model="claude-opus-4-6",
            max_tokens=1024,
            cache_control={ "type": "ephemeral" },
            output_config={"effort": "low"},
            system=system_prompt,
            messages=messages,
            tools=tool_schemas,
        )
        if container_id is not None:
            # Reuse the server-side code-execution container so web_search's
            # pending tool uses can resume across turns.
            request_kwargs["container"] = container_id


        async with client.messages.stream(**request_kwargs) as stream:
            print(f"=== Agent reasoning: ===")
            print("*** ", end=" ")
            # Iterate raw events (not just text_stream) so we can capture the
            # code-execution container id: the GA stream helper drops it from
            # the accumulated final message, but it arrives on message_delta.
            async for event in stream:
                if event.type == "text":
                    print(event.text, end="", flush=True)
                elif event.type == "message_delta" and event.delta.container is not None:
                    container_id = event.delta.container.id
            print()  # newline after streamed text

            message = await stream.get_final_message()  # full reconstructed message


        stop_reason = message.stop_reason
        #print(f"=== Stop reason: {stop_reason} ===")
        print(f"\n=== Agent determination: {stop_reason} ===")
        if stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": message.content})
            continue          # resend so the server-side search can finish
        if stop_reason != "tool_use":
            break

        tool_results = []
        for block in message.content:
            if block.type == "tool_use":
                #print(f"=== Using tool {block.name} with input {block.input} ===")
                print(f"=== Action: {block.name} ===")
                print(f"=== Action input: {block.input} ===")
                fn = tools[block.name]["fn"]
                result = fn(**block.input)
                print(f"=== Action result: {result} ===")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
        messages.append({"role": "assistant", "content": message.content})  # add messages to the short memory context
        messages.append({"role": "user", "content": tool_results})

        print(f"\n=== Back to you: ===")


