from langgraph.graph import StateGraph, START, END, MessagesState
from typing import TypedDict, Annotated
import operator
from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
import os  # Import os module to set environment variables

llm = ChatGroq(temperature=0, model="Llama-3.3-70b-Specdec", api_key="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")

system_prompt = """You are a helpful chatbot. You can help users with their questions.You can also ask questions to clarify the user's intent. You can also provide information to the user."""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def call_llm(state: AgentState):
    messages = state["messages"]
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {"messages": [message]}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)
agent = graph.compile()

# Visualize the graph
from IPython.display import Image, display
display(Image(agent.get_graph().draw_mermaid_png()))

# Test it



from langchain_community.tools.tavily_search import TavilySearchResults

# Set the environment variable for the API key
os.environ["TAVILY_API_KEY"] = "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"

tool = TavilySearchResults(max_results=4)  # No need to pass the API key directly
print(type(tool))
print(tool.name)
tools = [tool]


model = llm.bind_tools(tools)
tools_map = {tool.name: tool for tool in tools}

def call_llm(state: AgentState):
    messages = state['messages']
    messages = [SystemMessage(content=system_prompt)] + messages
    message = model.invoke(messages)
    return {'messages': [message]}

def take_action(state: AgentState):
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for tool_call in tool_calls:
        print(f"Calling {tool_call['name']} with {tool_call['args']}")
        if not tool_call['name'] in tools_map:
            print("n....bad tool name....")
            result = "bad tool name, retry"
        else:
            result = tools_map[tool_call['name']].invoke(tool_call['args'])
        results.append(ToolMessage(tool_call_id=tool_call['id'], name=tool_call['name'], content=str(result)))
    print("Back to model!")
    return {"messages": results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("action", take_action)

def route_action(state: AgentState):
    result = state['messages'][-1]
    return len(result.tool_calls) > 0

graph.add_conditional_edges(
    "llm",
    route_action,
    {True: "action", False: END}
)
graph.add_edge("action", "llm")
graph.set_entry_point("llm")
graph = graph.compile()

# Visualize the workflow
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))



# User input section with repetition
while True:
    user_input = input("Please enter your question (or type 'exit' to quit): ")  # Prompt the user for input
    if user_input.lower() == 'exit':  # Check if the user wants to exit
        print("Exiting the program.")
        break  # Exit the loop
    messages = [HumanMessage(content=user_input)]  # Create a HumanMessage with the user's input
    result = graph.invoke({"messages": messages})  # Invoke the graph with the user's message
    print(result['messages'][-1].content)  # Print the model's response