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
llm = ChatGroq(temperature=0, model="Llama-3.3-70b-Specdec", api_key="YOUR_API_KEY")

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

# Visualize the graph
from IPython.display import Image, display
display(Image(agent.get_graph().draw_mermaid_png()))

# Test it



from langchain_community.tools.tavily_search import TavilySearchResults

# Set the environment variable for the API key
os.environ["TAVILY_API_KEY"] = "YOUR_API_KEY"

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message')
    
    # Check if the user is asking for the current time
    if "time" in user_message.lower():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current time
        response_text = f"The current time is: {current_time}"
    else:
        try:
            # Process the message and generate a response
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
            response = llm.invoke(messages)  # Call your LLM to get a response
            
            # Access the content directly from the response
            response_text = response.content if hasattr(response, 'content') else 'No response content available.'
        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error for debugging
            response_text = "Sorry, I couldn't process your request at the moment. Please try again later."

    return jsonify({'response': response_text})  # Return the response

@app.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt')
    
    # Call the Hugging Face image generation API
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",  # Example model endpoint
            headers={
                "Authorization": f"Bearer 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",  # Your Hugging Face token
                "Content-Type": "application/json"
            },
            json={
                "inputs": prompt,
                "options": {"use_cache": False}  # Optional: Disable caching
            }
        )
        
        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()
            image_url = response_data['generated_images'][0]  # Adjust based on the API response structure
        else:
            print(f"Error: {response.status_code}, {response.text}")
            image_url = None
    except Exception as e:
        print(f"Error occurred: {e}")
        image_url = None

    return jsonify({'image_url': image_url})  # Return the image URL

if __name__ == '__main__':
    app.run(debug=True)  # Run in debug mode for development
