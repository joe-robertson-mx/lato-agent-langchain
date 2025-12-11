"""Helpers to pretty-print and save agent runs for terminal readability.

Provides optional rich-based output and file saving (JSON + Markdown).
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


class LangChainJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles LangChain message objects and other non-serializable types."""

    def default(self, obj: Any) -> Any:
        # Handle LangChain message types by converting to dict
        if hasattr(obj, "model_dump"):
            # Pydantic v2 models
            return obj.model_dump()
        if hasattr(obj, "dict"):
            # Pydantic v1 models or similar
            return obj.dict()
        if hasattr(obj, "__dict__"):
            # Generic objects with __dict__
            return obj.__dict__
        # Fallback to string representation
        return str(obj)


try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
except Exception:
    Console = None
    Markdown = None
    Panel = None


def find_repair_summary(run: Any) -> Optional[str]:
    """Attempt to extract the "Repair Request Summary" text from a run object.

    Looks for message-like dicts with a `content` value and returns the first
    content that contains the marker text.
    """
    marker = "Repair Request Summary"

    # Helper to inspect an item for content
    def content_of(item: Any) -> Optional[str]:
        if isinstance(item, dict):
            for k in ("content", "text", "message", "output"):
                v = item.get(k)
                if isinstance(v, str) and marker in v:
                    return v
        return None

    if isinstance(run, dict):
        # common case: run has a 'messages' list
        messages = run.get("messages") or run.get("generations") or run.get("choices")
        if isinstance(messages, list):
            for m in messages:
                v = content_of(m)
                if v:
                    return v
                # Some tool messages may carry 'content' as nested JSON string
                if isinstance(m, dict):
                    for val in m.values():
                        if isinstance(val, str) and marker in val:
                            return val

        # Fallback: scan entire dict for strings containing the marker
        def scan(d: Dict[str, Any]) -> Optional[str]:
            for _, v in d.items():
                if isinstance(v, str) and marker in v:
                    return v
                if isinstance(v, dict):
                    r = scan(v)
                    if r:
                        return r
                if isinstance(v, list):
                    for it in v:
                        if isinstance(it, dict):
                            r = scan(it)
                            if r:
                                return r
            return None

        return scan(run)

    return None


def rich_print_run(run: Any) -> None:
    """Pretty-print a run using rich if available, otherwise fallback to JSON."""
    if Console is None:
        try:
            output = json.dumps(run, indent=2, ensure_ascii=False, cls=LangChainJSONEncoder)
            print(output)
        except Exception as e:
            print(f"Could not serialize to JSON: {e}")
            print(run)
        return

    console = Console()

    # If run contains messages, print them in sequence
    if isinstance(run, dict) and (run.get("messages") or run.get("generations") or run.get("choices")):
        messages = run.get("messages") or run.get("generations") or run.get("choices")
        for m in messages:
            role = m.get("role") or m.get("name") or m.get("type") or "message"
            content = m.get("content") if isinstance(m, dict) else str(m)
            console.rule(f"[bold cyan]{role}")
            if Markdown and ("\n" in content or len(content) > 200):
                console.print(Markdown(content))
            else:
                console.print(content)
    else:
        # Fallback: print the whole run as JSON inside a panel
        try:
            j = json.dumps(run, indent=2, ensure_ascii=False, cls=LangChainJSONEncoder)
            console.print(Panel(j, title="Agent Run (raw JSON)", subtitle=datetime.utcnow().isoformat()))
        except Exception as e:
            console.print(f"Could not serialize run to JSON: {e}")


def print_repair_summary(summary_text: Optional[str]) -> None:
    """Print the Repair Request Summary text nicely (Markdown if possible)."""
    if summary_text is None:
        print("(no repair summary found in run)")
        return

    if Console is None or Markdown is None:
        print(summary_text)
        return

    console = Console()
    console.rule("[bold green]Repair Request Summary")
    console.print(Markdown(summary_text))


def save_run(run: Any, summary_text: Optional[str], logs_dir: str = "logs") -> Tuple[str, Optional[str]]:
    """Save the raw run as JSON and the summary as Markdown (if present).

    Returns tuple (json_path, md_path_or_None).
    """
    os.makedirs(logs_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = os.path.join(logs_dir, f"agent_run_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2, ensure_ascii=False, cls=LangChainJSONEncoder)

    md_path = None
    if summary_text:
        md_path = os.path.join(logs_dir, f"agent_run_{ts}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Agent Run {ts}\n\n")
            f.write(summary_text)

    return json_path, md_path
