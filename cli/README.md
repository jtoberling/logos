# Logos CLI Client

Command-line interface for interacting with Logos using local LLMs.

## Installation

```bash
pip install -e .
```

## Usage

### Interactive Chat

Start an interactive chat session with Logos:

```bash
# Using Ollama (default)
logos-cli chat --llm ollama --model llama2

# Using LMStudio
logos-cli chat --llm lmstudio --model local-model --base-url http://localhost:1234/v1

# Using OpenAI
logos-cli chat --llm openai --model gpt-4 --api-key your-api-key

# Using Anthropic Claude
logos-cli chat --llm anthropic --model claude-3-sonnet-20240229 --api-key your-api-key

# Using Google Gemini
logos-cli chat --llm gemini --model gemini-pro --api-key your-api-key
```

### Single Query

Ask a single question:

```bash
logos-cli query "What is the KISS principle?" --llm ollama --model llama2
```

### Get Raw Context

Get raw context from Logos without LLM processing:

```bash
logos-cli context "What are our development guidelines?"
```

### Get Constitution

View Logos' personality constitution:

```bash
logos-cli constitution
```

## Configuration

### Server Connection

By default, the CLI connects to `http://localhost:8000`. Change this with:

```bash
logos-cli --server http://your-logos-server:8000 chat --llm ollama --model llama2
```

### LLM Providers

#### Ollama (Local)
```bash
logos-cli chat --llm ollama --model llama2 --base-url http://localhost:11434
```

#### LMStudio (Local)
```bash
logos-cli chat --llm lmstudio --model local-model --base-url http://localhost:1234/v1
```

#### OpenAI (Cloud)
```bash
export OPENAI_API_KEY=your-key
logos-cli chat --llm openai --model gpt-4
```

#### Anthropic (Cloud)
```bash
export ANTHROPIC_API_KEY=your-key
logos-cli chat --llm anthropic --model claude-3-sonnet-20240229
```

#### Google Gemini (Cloud)
```bash
export GOOGLE_API_KEY=your-key
logos-cli chat --llm gemini --model gemini-pro
```

## Requirements

- Python 3.8+
- Logos MCP server running
- LLM provider (local or cloud API)

## Dependencies

See `requirements.txt` for the full list. Core dependencies include:

- `click` - CLI framework
- `httpx` - HTTP client
- Provider-specific libraries (openai, anthropic, google-generativeai, etc.)

## Architecture

The CLI client:

1. Connects to the Logos MCP server via HTTP
2. Queries for relevant context and constitution
3. Sends combined context to configured LLM
4. Displays the LLM's response

This keeps the core Logos server pure (memory engine only) while providing a convenient interface for testing and interaction.