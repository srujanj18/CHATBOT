from langgraph.graph import StateGraph, START, END, MessagesState
from typing import TypedDict, Annotated
import operator
from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
import os  # Import os module to set environment variables
from flask import Flask, render_template, request, jsonify
from datetime import datetime  # Import datetime module
import requests  # Import requests to make API calls

app = Flask(__name__)

# Initialize your LLM and other components here
llm = ChatGroq(temperature=0, model="Llama-3.3-70b-Specdec", api_key="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")

system_prompt = """You are a helpful chatbot. You can help users with their questions."""

class AgentState(TypedDict):
    messages: list[AnyMessage]

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

from langchain_community.tools.tavily_search import TavilySearchResults

# Set the environment variable for the API key
os.environ["TAVILY_API_KEY"] = "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"

tool = TavilySearchResults(max_results=4)  # No need to pass the API key directly
tools = [tool]

model = llm.bind_tools(tools)
tools_map = {tool.name: tool for tool in tools}

def take_action(state: AgentState):
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for tool_call in tool_calls:
        if tool_call['name'] not in tools_map:
            result = "bad tool name, retry"
        else:
            result = tools_map[tool_call['name']].invoke(tool_call['args'])
        results.append(ToolMessage(tool_call_id=tool_call['id'], name=tool_call['name'], content=str(result)))
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message')
    
    if "time" in user_message.lower():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_text = f"The current time is: {current_time}"
    else:
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
            response = llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else 'No response content available.'
        except Exception as e:
            response_text = "Sorry, I couldn't process your request at the moment. Please try again later."

    return jsonify({'response': response_text})

# ... existing code ...

@app.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt')
    
    # Directly use API key (for demonstration purposes only)
    hugging_face_token = "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"  # API key hardcoded

    headers = {
        "Authorization": f"Bearer {hugging_face_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
            headers=headers,
            json={"inputs": prompt}
        )

        if response.status_code == 200:
            filename = f"generated_{int(datetime.now().timestamp())}.png"
            with open(filename, "wb") as file:
                file.write(response.content)
            return jsonify({'image_url': f"/static/{filename}"})
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return jsonify({'error': 'Image generation failed'}), 500

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return jsonify({'error': 'Image generation failed'}), 500

# ... rest of the existing code ...


if __name__ == '__main__':
    app.run(debug=True)
