import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from tools import tools

Path("data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv(
    "DEFAULT_CHAT_MODEL",
    os.getenv("GOOGLE_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
)

MODEL_CATALOG = {
    "gemini-2.5-flash": {
        "label": "Gemini 2.5 Flash",
        "provider": "google",
        "description": "Fast, capable everyday assistant",
        "env_var": "GOOGLE_API_KEY",
    },
    "gemini-2.5-pro": {
        "label": "Gemini 2.5 Pro",
        "provider": "google",
        "description": "Advanced reasoning and complex tasks",
        "env_var": "GOOGLE_API_KEY",
    },
    "gemini-2.5-flash-lite": {
        "label": "Gemini 2.5 Flash Lite",
        "provider": "google",
        "description": "Lightweight and cost efficient",
        "env_var": "GOOGLE_API_KEY",
    },
    "gpt-5.4-mini": {
        "label": "GPT-5.4 mini",
        "provider": "openai",
        "description": "Strong OpenAI model for agentic work",
        "env_var": "OPENAI_API_KEY",
    },
    "chat-latest": {
        "label": "ChatGPT Latest",
        "provider": "openai",
        "description": "Latest ChatGPT Instant model",
        "env_var": "OPENAI_API_KEY",
    },
}

ALLOWED_MODELS = set(MODEL_CATALOG)

if DEFAULT_MODEL not in ALLOWED_MODELS:
    DEFAULT_MODEL = "gemini-2.5-flash"


class ModelConfigurationError(ValueError):
    """Raised when the selected model provider is not configured."""


def get_model_catalog() -> list[dict]:
    """Return safe model metadata for the frontend (never API key values)."""
    return [
        {
            "id": model_id,
            "label": config["label"],
            "provider": config["provider"],
            "description": config["description"],
            "available": bool(os.getenv(config["env_var"])),
            "is_default": model_id == DEFAULT_MODEL,
        }
        for model_id, config in MODEL_CATALOG.items()
    ]



SYSTEM_PROMPT = """
You are a helpful Agentic AI assistant named LunarkChat similar to ChatGPT.

You can:
1. Answer normal questions.
2. Use tools when needed.
3. Search uploaded documents using the RAG tool.
4. Search the web for latest/current information using Tavily Search.
5. Remember important user information using the memory tool.
6. Recall memory when useful.
7. Use calculator for math.

Rules:
- If the user asks about latest news, current events, recent updates, today's information, current prices, current people, current versions, new releases, or anything time-sensitive, use Tavily Search.
- If the user asks about an uploaded document, use search_uploaded_documents.
- If the user asks you to remember something, use remember_this.
- If the user asks about previous preferences or saved facts, use recall_memory.
- Use calculator for math questions.
- When using web search, summarize clearly and mention that the answer is based on web search results.
- Be clear, helpful, and concise.
"""



def normalize_model_name(model_name: str | None) -> str:
    """
    Validate selected model from frontend.
    If model is missing or not allowed, fallback to DEFAULT_MODEL.
    """

    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()

    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name




def build_agent(model_name: str):
    """
    Build one LangGraph agent for the selected provider and model.
    """

    selected_model = normalize_model_name(model_name)
    model_config = MODEL_CATALOG[selected_model]
    required_env_var = model_config["env_var"]

    if not os.getenv(required_env_var):
        provider_name = model_config["provider"].title()
        raise ModelConfigurationError(
            f"{provider_name} is not configured. Add {required_env_var} to your .env file."
        )

    if model_config["provider"] == "google":
        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            temperature=0.3,
            streaming=True,
        )
    elif model_config["provider"] == "openai":
        llm = ChatOpenAI(
            model=selected_model,
            streaming=True,
        )
    else:
        raise ModelConfigurationError("Unsupported model provider.")

    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    workflow = StateGraph(MessagesState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "chatbot")
    workflow.add_conditional_edges("chatbot", tools_condition)
    workflow.add_edge("tools", "chatbot")

    conn = sqlite3.connect(
        "data/langgraph_checkpoints.sqlite",
        check_same_thread=False
    )

    checkpointer = SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)


_AGENT_CACHE = {}


def get_agent(model_name: str | None = None):
    """
    Return cached LangGraph agent for selected model.
    If not created yet, create it once and reuse it.
    """

    selected_model = normalize_model_name(model_name)

    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = build_agent(selected_model)

    return _AGENT_CACHE[selected_model]
