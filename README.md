# LunarkChat

LunarkChat is a multi-model agentic AI workspace built with FastAPI, LangGraph, and LangChain. It combines streaming chat, document question answering, web search, long-term memory, and persistent conversations in a responsive web interface.

## Highlights

- Select models from Google Gemini and OpenAI.
- Stream assistant responses in real time with Server-Sent Events (SSE).
- Upload PDF, DOCX, TXT, Markdown, Python, and CSV files.
- Search uploaded documents with retrieval-augmented generation (RAG).
- Search the live web with Tavily when current information is needed.
- Save and recall user information with thread-scoped long-term memory.
- Resume previous conversations from the sidebar.
- Permanently delete individual conversations from the sidebar.
- Use the responsive dark interface on desktop and mobile.
- Run locally, in Docker, or through the included AWS deployment workflow.

## Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn |
| Agent orchestration | LangGraph, LangChain |
| LLM providers | Google Gemini, OpenAI |
| Embeddings | Google Generative AI embeddings |
| Vector storage | ChromaDB |
| Application storage | SQLite, SQLAlchemy |
| Web search | Tavily |
| Frontend | Jinja2, HTML, CSS, JavaScript |
| Deployment | Docker, GitHub Actions, Amazon ECR, EC2 |

## Available Models

| Provider | Display name | Model ID |
| --- | --- | --- |
| Google | Gemini 2.5 Flash | `gemini-2.5-flash` |
| Google | Gemini 2.5 Pro | `gemini-2.5-pro` |
| Google | Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` |
| OpenAI | GPT-5.4 mini | `gpt-5.4-mini` |
| OpenAI | ChatGPT Latest | `chat-latest` |

Models remain visible in the selector when their provider is not configured, but they are disabled. API key values stay on the server and are never returned by the `/models` endpoint.

## Prerequisites

- Python 3.11
- Git
- At least one LLM provider API key
- A Google API key for document embeddings when using file upload and RAG
- A Tavily API key when using live web search
- Docker and an AWS account only if you plan to deploy

## Local Setup

### 1. Clone and enter the repository

```bash
git clone https://github.com/entbappy/BappyGPT.git
cd BappyGPT
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`, then replace the placeholder values you need.

```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional model and local-server defaults
DEFAULT_CHAT_MODEL=gemini-2.5-flash
APP_HOST=127.0.0.1
APP_PORT=8001

# Optional LangSmith tracing
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=LunarkChat
```

You only need an OpenAI key if you want to use OpenAI models. Google configuration is also required by the current RAG embedding implementation.

### 5. Start the application

```bash
python app.py
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001).

## Using LunarkChat

1. Select an available model from the model menu.
2. Start a new conversation or resume one from the sidebar.
3. Enter a message and press Enter to send it. Use Shift+Enter for a new line.
4. Upload a supported document and ask questions about its contents.
5. Ask for current information to let the agent use Tavily web search.
6. Ask the assistant to remember a fact when you want it stored as long-term memory.
7. Hover over a saved conversation and select the trash icon to delete it. The app asks for confirmation because deletion is permanent.

Example prompts:

```text
Summarize the document I uploaded and list the important action items.
```

```text
Search the web for the latest developments in AI agents.
```

```text
Remember that I prefer concise technical explanations.
```

```text
Calculate 125 * 48 / 6.
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Render the chat interface |
| `GET` | `/models` | Return model metadata and provider availability |
| `GET` | `/conversations` | List saved conversations |
| `GET` | `/history/{thread_id}` | Load messages from one conversation |
| `DELETE` | `/conversations/{thread_id}` | Delete a conversation and its thread-scoped data |
| `POST` | `/upload` | Ingest a document into the RAG collection |
| `POST` | `/chat/stream` | Stream an agent response over SSE |

## Data Storage

LunarkChat stores local runtime data in three places:

- `data/chatbot_memory.db` contains conversations, messages, and long-term memory.
- `data/langgraph_checkpoints.sqlite` contains LangGraph thread checkpoints.
- `chroma_db/` contains document embeddings and vector data.
- `uploads/` contains uploaded source files.

Deleting a conversation removes its database messages, thread-scoped memory, and LangGraph checkpoints. Uploaded files and their ChromaDB embeddings are not currently removed by the conversation delete action.

## Project Structure

```text
LunarkChat/
|-- app.py                  # FastAPI routes and SSE streaming
|-- agent.py                # Model catalog and LangGraph workflow
|-- database.py             # Conversations, history, memory, and deletion
|-- rag.py                  # File extraction, chunking, embeddings, retrieval
|-- tools.py                # RAG, memory, calculator, and Tavily tools
|-- requirements.txt        # Python dependencies
|-- Dockerfile              # Production container definition
|-- .env.example            # Environment variable template
|-- templates/
|   `-- index.html          # Responsive chat interface
|-- data/                   # SQLite application data
|-- chroma_db/              # Persistent vector store
`-- uploads/                # Uploaded documents
```

## Docker

Build the image:

```bash
docker build -t lunarkchat .
```

Run the container:

```bash
docker run -d \
  --name lunarkchat \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  lunarkchat
```

Open [http://localhost:8080](http://localhost:8080).

For persistent production data, mount volumes for `/app/data`, `/app/chroma_db`, and `/app/uploads`.

## Vercel Deployment

Vercel automatically detects the FastAPI application exported as `app` in `app.py`. Connect this repository to a Vercel project and configure the provider environment variables before deploying.

Vercel Functions expose a read-only application filesystem, so LunarkChat writes SQLite databases, LangGraph checkpoints, ChromaDB files, and uploaded documents beneath `/tmp/lunarkchat` when `VERCEL=1` is present. This prevents function-startup crashes, but `/tmp` is ephemeral and is not shared reliably between function instances.

The Vercel deployment is therefore suitable for demonstrations and temporary sessions. For persistent production conversations and document retrieval, replace local storage with managed services such as PostgreSQL/Neon or Supabase, pgvector or another hosted vector database, and object storage such as Vercel Blob.

## AWS CI/CD

The workflow at `.github/workflows/cicd.yaml` builds the Docker image, pushes it to Amazon ECR, and deploys it to an EC2 self-hosted runner when changes are pushed to `main`.

Configure these GitHub Actions secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
ECR_REPO
GOOGLE_API_KEY
OPENAI_API_KEY
DEFAULT_CHAT_MODEL
TAVILY_API_KEY
LANGSMITH_TRACING
LANGSMITH_ENDPOINT
LANGSMITH_API_KEY
LANGSMITH_PROJECT
```

The EC2 security group must allow TCP port `8080` from the networks that should access the application.

## Troubleshooting

### Windows `[WinError 10013]`

The configured port is blocked, reserved, or already controlled by another Windows service. Start LunarkChat on another port:

```powershell
$env:APP_PORT="8002"
python app.py
```

Then open `http://127.0.0.1:8002`. You can also set `APP_PORT=8002` permanently in `.env`.

### A model is disabled

Add the corresponding provider key to `.env` and restart the server. The application reads environment variables when the process starts.

### Document search returns no content

Make sure the document was uploaded in the same conversation thread. RAG documents are filtered by `thread_id`, so another conversation cannot retrieve them.

## Security Notes

- Never commit `.env` or real API keys.
- Store production secrets in GitHub Actions or another secret manager.
- Restrict EC2 security-group access for production deployments.
- Uploaded documents and local databases may contain sensitive information; protect and back them up appropriately.
- Rotate any credentials that have been exposed publicly.

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, make and test your changes, and submit a pull request.

## License

This project is open source. Review the repository license before distribution or commercial use.
