"""
SAI-OS AI Shell — Main CLI Entry Point.

The primary user interface for SAI-OS. Supports:
- Interactive REPL mode: `sai`
- One-shot mode: `sai "open firefox"`
- Pipe mode: `echo "check health" | sai`

Replaces the traditional terminal with natural language interaction.
"""

from __future__ import annotations

import asyncio
import sys

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from sai_core.config import SAI_DATA_DIR, get_config
from sai_core.shell.completer import SAICompleter
from sai_core.shell.formatter import (
    clear_thinking,
    console,
    print_actions_summary,
    print_confirm,
    print_error,
    print_response,
    print_success,
    print_thinking,
    print_warning,
    print_welcome,
)

PROMPT_STYLE = Style.from_dict({
    "prompt": "ansicyan bold",
    "": "ansiwhite",
})


async def _run_interactive() -> None:
    """Run the interactive SAI Shell REPL."""
    from sai_core.brain.engine import SAIBrain

    brain = SAIBrain()
    config = get_config()
    completer = SAICompleter()

    # Ensure history dir exists
    history_file = SAI_DATA_DIR / "shell_history"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    session: PromptSession = PromptSession(
        history=FileHistory(str(history_file)),
        completer=completer,
        style=PROMPT_STYLE,
        complete_while_typing=True,
    )

    print_welcome()

    # Initialize brain
    backend_info = f"{config.llm.backend} @ {config.llm.host} ({config.llm.default_model})"
    console.print(f"  [dim]Connecting to {backend_info}...[/]", end="\r")
    ok = await brain.initialize()
    if ok:
        console.print(f"  [green]✅ AI engine ready — {brain.backend_name}[/]          ")
    else:
        print_warning(f"Cannot connect to {config.llm.backend} at {config.llm.host}")
        print_warning("Edit ~/.config/sai/config.toml to configure your LLM backend")
        print_warning("Supported: openai (copilot-api/LM Studio), ollama, anthropic")

    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: session.prompt(
                    [("class:prompt", f"{config.shell.prompt_symbol} ")],
                ),
            )
        except (EOFError, KeyboardInterrupt):
            console.print("\n  [sai.info]Goodbye! 👋[/]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        # Built-in commands
        if user_input.lower() in ("exit", "quit", "bye"):
            console.print("  [sai.info]Goodbye! 👋[/]")
            break
        elif user_input.lower() == "clear":
            console.clear()
            continue
        elif user_input.lower() == "help":
            _print_help()
            continue
        elif user_input.lower() == "reset":
            brain.clear_context()
            print_success("Context cleared.")
            continue

        completer.add_to_history(user_input)
        print_thinking()

        try:
            result = await brain.process(user_input)
        except Exception as e:
            clear_thinking()
            print_error(f"Processing failed: {e}")
            continue

        clear_thinking()

        # Handle confirmation-required actions
        if result.get("requires_confirmation"):
            confirmed = print_confirm(result["confirm_message"])
            if confirmed:
                result = await brain.confirm_and_execute(
                    result["pending_function"],
                    result["pending_arguments"],
                )
            else:
                print_warning("Cancelled.")
                continue

        # Display response
        print_response(result.get("response", ""))
        print_actions_summary(result.get("actions", []))
        console.print()

    brain.shutdown()


async def _run_oneshot(command: str) -> None:
    """Run a single command and exit."""
    from sai_core.brain.engine import SAIBrain

    brain = SAIBrain()
    ok = await brain.initialize()
    if not ok:
        config = get_config()
        print_error(
            f"Cannot connect to {config.llm.backend} at {config.llm.host}. "
            "Check your config: ~/.config/sai/config.toml"
        )
        sys.exit(1)

    result = await brain.process(command)

    if result.get("requires_confirmation"):
        confirmed = print_confirm(result["confirm_message"])
        if confirmed:
            result = await brain.confirm_and_execute(
                result["pending_function"],
                result["pending_arguments"],
            )
        else:
            print_warning("Cancelled.")
            brain.shutdown()
            return

    print_response(result.get("response", ""))
    brain.shutdown()


def _print_help() -> None:
    """Print help information."""
    console.print("""
  [bold cyan]SAI-OS Shell — Help[/]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Just type what you want in natural language!

  [bold]Examples:[/]
    • "open firefox"
    • "install vlc"
    • "clean my system"
    • "organize my downloads"
    • "check system health"
    • "play some music"
    • "prepare my work setup"
    • "find large files"
    • "what's running right now"

  [bold]Commands:[/]
    • [cyan]clear[/]   — Clear the screen
    • [cyan]reset[/]   — Reset conversation context
    • [cyan]help[/]    — Show this help
    • [cyan]exit[/]    — Exit SAI Shell
""")


@click.command()
@click.argument("command", nargs=-1, required=False)
@click.option("--model", "-m", default=None, help="LLM model to use")
@click.option("--backend", "-b", default=None, help="LLM backend: openai, ollama, anthropic")
@click.option("--host", "-H", default=None, help="LLM API host URL")
@click.option("--api-key", "-k", default=None, help="API key for the LLM backend")
@click.version_option(version="0.1.0", prog_name="SAI-OS")
def main(
    command: tuple[str, ...],
    model: str | None,
    backend: str | None,
    host: str | None,
    api_key: str | None,
) -> None:
    """SAI-OS — AI-powered operating system shell.

    Run without arguments for interactive mode, or pass a command:

    \b
        sai "open firefox"
        sai check system health
        sai --backend ollama --host http://localhost:11434 "hello"
        sai --backend openai --host http://localhost:4141 -m gpt-4o
    """
    config = get_config()
    if model:
        config.llm.default_model = model
    if backend:
        config.llm.backend = backend
    if host:
        config.llm.host = host
    if api_key:
        config.llm.api_key = api_key

    if command:
        cmd = " ".join(command)
        asyncio.run(_run_oneshot(cmd))
    elif not sys.stdin.isatty():
        # Pipe mode
        cmd = sys.stdin.read().strip()
        if cmd:
            asyncio.run(_run_oneshot(cmd))
    else:
        asyncio.run(_run_interactive())


if __name__ == "__main__":
    main()
