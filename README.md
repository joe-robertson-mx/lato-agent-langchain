(The file `c:\Users\Joe.Robertson\Documents\Projects\lato-agent-langchain\README.md` exists, but is empty)
# Lato Agent (langchain) — demo

Lightweight project demonstrating a LangChain-based agent for handling customer return/repair requests.

 What's included
 - `main.py` — centralized CLI entrypoint to run built-in agents.
 - `app/api.py` — FastAPI wrapper exposing the return-request agent over HTTP.
 - `requirements.txt` — optional requirements list (if you prefer pip). This project prefers the `uv` package manager.
 - `.env` — local environment file (ignored by git). Put API keys here.

 Quick local setup (using `uv`)

 1. Ensure you have Python 3.11+ and the `uv` package manager installed and configured for this project. `uv` is used for dependency management and to run scripts in this repository. If you don't have it, follow your usual installation method for `uv`.

 2. Add the project dependencies with `uv`. Example (adds the commonly used packages):
 ```bash
 uv add python-dotenv rich requests langchain langchain-openai langgraph
 ```

 3. Add credentials to `./.env` (replace placeholders):
 ```bash
 export OPENAI_API_KEY=<your-openai-api-key>
 export LANGSMITH_API_KEY=<your-langsmith-api-key>
 ```

 Notes:
 - If you prefer `pip` and a venv, `requirements.txt` is provided, but this repository's examples use `uv run`.

2. Add credentials to `./.env` (example keys already present — replace placeholders):
```
export OPENAI_API_KEY=<your-openai-api-key>
export LANGSMITH_API_KEY=<your-langsmith-api-key>
```

 Running agents from CLI (use `uv`)
 - Run the return-request agent (pretty output):
 ```bash
 uv run main.py --run-return-request --from-field "Jane Doe <jane@example.com>" \
	 --content "My motor makes a grinding noise and the bike won't pedal." --format pretty
 ```

 - Save the run (JSON + Markdown summary saved to `logs/`):
 ```bash
 uv run main.py --run-return-request --save
 ```

 
Notes and troubleshooting
- The agents use `langchain` and may require `langgraph` as an optional dependency. If you see import errors like `No module named 'langgraph.prebuilt.tool_node'`, install `langgraph`:
```bash
uv add langgraph
# or
pip install langgraph
```
- Long outputs are saved to `logs/agent_run_<timestamp>.json` (raw) and `logs/agent_run_<timestamp>.md` (Markdown summary). Use the Markdown file to send concise instructions to CSRs.

