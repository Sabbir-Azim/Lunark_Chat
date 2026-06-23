# BappyGPT

BappyGPT is an open-source, agentic AI chatbot project built with Python, FastAPI, LangGraph, and Google Gemini. It supports conversational chat, document uploads, retrieval-augmented generation (RAG), web search, memory, and a simple web UI.

## Features

- Chat with an AI agent powered by Google Gemini
- Stream responses in real time
- Upload documents such as PDF, DOCX, TXT, MD, PY, and CSV
- Use uploaded files as context through RAG
- Search the web with Tavily for current information
- Store and recall user memories in conversation threads
- Simple FastAPI-based web interface

## Project Overview

This project combines:

- FastAPI for the web server and API endpoints
- Jinja2 templates for the frontend UI
- LangGraph for agent orchestration
- LangChain tools for web search, memory, and document retrieval
- ChromaDB for vector search over uploaded documents
- SQLite for conversation and checkpoint persistence

## Prerequisites

- Python 3.11
- pip or conda
- Google API key for Gemini
- Tavily API key for web search
- Optional: Docker and an AWS account for deployment

## How to run BappyGPT

### 1. Clone the repository

`ash
git clone https://github.com/entbappy/BappyGPT.git
`

### 2. Navigate to the project directory

`ash
cd BappyGPT
`

### 3. Create a virtual environment (optional but recommended)

`ash
conda create -n bappygpt python=3.11 -y
`

### 4. Activate the virtual environment

`ash
conda activate bappygpt
`

### 5. Install the required dependencies

`ash
pip install -r requirements.txt
`

### 6. Set up environment variables

Create a .env file in the project root with the required values:

`env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-2.5-flash
TAVILY_API_KEY=your_tavily_api_key

LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=bappygpt
`

> If you do not want to use LangSmith, you can leave those values unset or set LANGSMITH_TRACING=false.

### 7. Run the application

`ash
python app.py
`

The app will be available at:

`	ext
http://127.0.0.1:8000
`

## Project Structure

`	ext
agent.py           # LangGraph agent setup and tool orchestration
app.py             # FastAPI app and streaming chat endpoints
database.py        # Conversation and memory persistence
rag.py             # Document ingestion and RAG search logic
tools.py           # Agent tools such as calculator, memory, web search, and RAG
templates/         # HTML templates for the UI
uploads/           # Uploaded documents
chroma_db/         # Vector database storage
`

## Usage

- Open the web app in your browser.
- Start chatting with the assistant.
- Upload documents to give the agent context from your own files.
- Ask questions that require current information and the agent will use web search.

## AWS CI/CD deployment with GitHub Actions

The following workflow is useful for deploying this project to AWS using Docker, ECR, and EC2.

### 1. Log in to the AWS console

### 2. Create an IAM user for deployment

Grant the user access for:

1. EC2 access (virtual machine)
2. ECR access (Elastic Container Registry to store your Docker image)

Recommended policies:

1. AmazonEC2ContainerRegistryFullAccess
2. AmazonEC2FullAccess

### 3. Create an ECR repository

Create a repository to store your Docker image and save the repository URI.

Example:

`	ext
315865595366.dkr.ecr.us-east-1.amazonaws.com/bappygpt
`

### 4. Create an EC2 machine (Ubuntu)

### 5. Install Docker on the EC2 instance

Optional update commands:

`ash
sudo apt-get update -y
sudo apt-get upgrade -y
`

Required Docker installation:

`ash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
`

### 6. Configure the EC2 instance as a GitHub self-hosted runner

Go to your GitHub repository settings, then Actions > Runners > New self-hosted runner, and follow the instructions for your OS.

### 7. Set up GitHub secrets

Add the following secrets in your repository settings:

- GOOGLE_API_KEY
- GOOGLE_MODEL
- TAVILY_API_KEY
- LANGSMITH_TRACING
- LANGSMITH_ENDPOINT
- LANGSMITH_API_KEY
- LANGSMITH_PROJECT
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- ECR_REPO

## Contributing

Contributions are welcome. If you would like to improve the project, please open an issue or submit a pull request.

## License

This project is open source. Please check the repository license for usage terms.