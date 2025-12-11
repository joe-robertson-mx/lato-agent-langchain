import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


class LangChainJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except Exception:
                pass
        if hasattr(obj, "dict"):
            try:
                return obj.dict()
            except Exception:
                pass
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


def find_repair_summary(run: Any) -> Optional[str]:
    marker = "Repair Request Summary"

    def content_of(item: Any) -> Optional[str]:
        if isinstance(item, dict):
            for k in ("content", "text", "message", "output"):
                v = item.get(k)
                if isinstance(v, str) and marker in v:
                    return v
        return None

    if isinstance(run, dict):
        messages = run.get("messages") or run.get("generations") or run.get("choices")
        if isinstance(messages, list):
            for m in messages:
                v = content_of(m)
                if v:
                    return v
                if isinstance(m, dict):
                    for val in m.values():
                        if isinstance(val, str) and marker in val:
                            return val

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
    console = Console()

    if isinstance(run, dict) and (run.get("messages") or run.get("generations") or run.get("choices")):
        messages = run.get("messages") or run.get("generations") or run.get("choices")
        for m in messages:
            role = m.get("role") or m.get("name") or m.get("type") or "message"
            content = m.get("content") if isinstance(m, dict) else str(m)
            console.rule(f"[bold cyan]{role}")
            if "\n" in content or len(content) > 200:
                console.print(Markdown(content))
            else:
                console.print(content)
    else:
        try:
            j = json.dumps(run, indent=2, ensure_ascii=False, cls=LangChainJSONEncoder)
            console.print(Panel(j, title="Agent Run (raw JSON)", subtitle=datetime.utcnow().isoformat()))
        except Exception as e:
            console.print(f"Could not serialize run to JSON: {e}")


def print_repair_summary(summary_text: Optional[str]) -> None:
    if summary_text is None:
        print("(no repair summary found in run)")
        return

    console = Console()
    console.rule("[bold green]Repair Request Summary")
    console.print(Markdown(summary_text))


def save_run(run: Any, filename: str) -> None:
    os.makedirs(os.path.dirname(filename) or "", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2, ensure_ascii=False, cls=LangChainJSONEncoder)
