import asyncio

from tools import TOOLS
from agent import run_agent

#prompt = "I had 12 apples, and I lost a third. Then a friend gave me 2. How many apples do I have?"
#prompt = "in google cloud, when configuring Google Private Access, is necessary to do any configuration in cloud dns?"
#prompt = "What's the sum of the current temperatures in Paris and Berlin?"
#prompt = "Get the JSON response from `https://jsonplaceholder.typicode.com/todos/1` and tell me what the title of the first item is"
max_turns = 5


from tools import TOOLS
from agent import run_agent

SESSION = "session.json"

while True:
    user_input = input("\n>>> You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break
    #run_agent(user_input, TOOLS, session_file=SESSION)
    asyncio.run(run_agent(user_input, TOOLS, max_turns))

#run_agent(prompt, TOOLS, max_turns)