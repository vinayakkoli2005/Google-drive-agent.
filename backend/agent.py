from typing import Annotated, TypedDict
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

load_dotenv()

from backend.google_drive import search_drive_files

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@tool
def search_google_drive(q: str) -> list[dict]:
    """
    Search files in the designated Google Drive folder.
    The 'q' parameter must be a valid Google Drive search query string.
    Examples:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'budget'
    - modifiedTime > '2023-10-24T12:00:00'
    """
    return search_drive_files(q)

tools = [search_google_drive]

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    """The chatbot node that calls the LLM."""
    messages = state["messages"]
    # Ensure system message is present
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_msg = SystemMessage(content=(
            "You are a helpful AI assistant that searches for files in a Google Drive.\n\n"
            "Use the search_google_drive tool to find files based on the user's natural language request. "
            "Translate the request into a valid Google Drive 'q' query string. Examples:\n"
            "  - name contains 'report'\n"
            "  - mimeType = 'application/pdf'\n"
            "  - fullText contains 'budget'\n"
            "  - modifiedTime > '2024-01-01T00:00:00'\n\n"
            "When presenting results, format each file like this (use markdown):\n"
            "- **[filename](webViewLink)** — `mimeType` — Last modified: `modifiedTime`\n\n"
            "Always include a clickable link using the webViewLink field. "
            "If webContentLink is available (i.e. the file can be downloaded directly), "
            "also add a download link like: [(download)](webContentLink)\n\n"
            "If no files are found, say so clearly and suggest the user try a different search term. "
            "If the search returns an error about the service account, inform the user politely."
        ))
        messages = [sys_msg] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Build the LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

def run_agent(user_message: str, chat_history: list[BaseMessage] = None) -> dict:
    """Run the agent with the given user message and history."""
    if chat_history is None:
        chat_history = []
        
    messages = chat_history + [HumanMessage(content=user_message)]
    
    final_state = graph.invoke({"messages": messages})
    return {"messages": final_state["messages"]}
