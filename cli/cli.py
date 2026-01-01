#!/usr/bin/env python3
"""
Logos CLI Client - Command-line interface for interacting with Logos using local LLMs.

Usage:
    logos-cli chat --llm ollama --model llama2
    logos-cli query "What is KISS principle?" --server http://localhost:8000
"""

import json
import sys
from typing import Optional, Dict, Any
import click
from pathlib import Path

from .llm_client import create_llm_client
from .mcp_client import LogosMCPClient


class LogosCLI:
    """Main CLI application for Logos."""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.mcp_client = LogosMCPClient(server_url)
        self.llm_client: Optional[LLMClient] = None

    def set_llm_provider(self, provider: str, model: str, **kwargs):
        """Configure LLM provider."""
        self.llm_client = create_llm_client(provider=provider, model=model, **kwargs)

    def query_logos(self, question: str) -> Dict[str, Any]:
        """Query Logos for context."""
        return self.mcp_client.query_logos(question)

    def chat_with_logos(self, question: str) -> str:
        """Query Logos and get LLM response."""
        if not self.llm_client:
            raise ValueError("LLM provider not configured. Use --llm option.")

        # Get context from Logos
        context = self.query_logos(question)

        if "error" in context:
            return f"Error from Logos: {context['error']}"

        # Build prompt for LLM
        system_prompt = context.get("constitution", "")
        personality_memories = context.get("personality_memories", [])
        project_knowledge = context.get("project_knowledge", [])

        # Combine context
        context_text = ""
        if personality_memories:
            context_text += "\n\nPersonality Memories:\n" + "\n".join([
                f"- {mem['text']}" for mem in personality_memories
            ])

        if project_knowledge:
            context_text += "\n\nProject Knowledge:\n" + "\n".join([
                f"- {mem['text']}" for mem in project_knowledge
            ])

        full_prompt = f"{system_prompt}\n\nContext:{context_text}\n\nQuestion: {question}"

        # Get LLM response
        return self.llm_client.generate(full_prompt, system_prompt)

    def interactive_chat(self):
        """Start interactive chat session."""
        click.echo("🤖 Welcome to Logos Chat!")
        click.echo("Type 'quit' or 'exit' to end the session.")
        click.echo("-" * 50)

        while True:
            try:
                question = click.prompt("You")
                if question.lower() in ['quit', 'exit', 'q']:
                    break

                click.echo("Logos is thinking...")
                response = self.chat_with_logos(question)
                click.echo(f"Logos: {response}")
                click.echo("-" * 50)

            except KeyboardInterrupt:
                break
            except Exception as e:
                click.echo(f"Error: {e}", err=True)

        click.echo("Goodbye! 👋")


@click.group()
@click.option('--server', default='http://localhost:8000',
              help='Logos MCP server URL')
@click.pass_context
def cli(ctx, server):
    """Logos CLI - Chat with Logos using local LLMs."""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = LogosCLI(server)


@cli.command()
@click.argument('question')
@click.option('--llm', default='ollama', help='LLM provider (ollama, lmstudio, gemini, etc.)')
@click.option('--model', default='llama2', help='LLM model name')
@click.option('--api-key', help='API key for cloud providers')
@click.option('--base-url', help='Base URL for local LLM providers')
@click.pass_context
def query(ctx, question, llm, model, api_key, base_url):
    """Query Logos and get a response."""
    logos_cli = ctx.obj['cli']

    # Configure LLM
    kwargs = {}
    if api_key:
        kwargs['api_key'] = api_key
    if base_url:
        kwargs['base_url'] = base_url

    logos_cli.set_llm_provider(llm, model, **kwargs)

    try:
        response = logos_cli.chat_with_logos(question)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--llm', default='ollama', help='LLM provider (ollama, lmstudio, gemini, etc.)')
@click.option('--model', default='llama2', help='LLM model name')
@click.option('--api-key', help='API key for cloud providers')
@click.option('--base-url', help='Base URL for local LLM providers')
@click.pass_context
def chat(ctx, llm, model, api_key, base_url):
    """Start interactive chat with Logos."""
    logos_cli = ctx.obj['cli']

    # Configure LLM
    kwargs = {}
    if api_key:
        kwargs['api_key'] = api_key
    if base_url:
        kwargs['base_url'] = base_url

    logos_cli.set_llm_provider(llm, model, **kwargs)

    logos_cli.interactive_chat()


@cli.command()
@click.argument('question')
@click.pass_context
def context(ctx, question):
    """Get raw context from Logos (no LLM response)."""
    logos_cli = ctx.obj['cli']

    try:
        context = logos_cli.query_logos(question)
        click.echo(json.dumps(context, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def constitution(ctx):
    """Get Logos constitution."""
    logos_cli = ctx.obj['cli']

    try:
        constitution = logos_cli.mcp_client.get_constitution()
        click.echo(constitution)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Get Logos version and system information."""
    logos_cli = ctx.obj['cli']

    try:
        version_info = logos_cli.mcp_client.get_version()
        click.echo(json.dumps(version_info, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()