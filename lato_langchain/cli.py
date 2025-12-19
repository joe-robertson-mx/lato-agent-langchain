from dotenv import load_dotenv

load_dotenv()


def main():
    import argparse
    import json
    import os
    from datetime import datetime

    parser = argparse.ArgumentParser(description="lato-agent-langchain entrypoint")
    parser.add_argument(
        "--run-return-request",
        action="store_true",
        help="Run the return request agent defined in `lato_langchain.agents.return_request_agent`",
    )
    parser.add_argument(
        "--run-agent",
        action="store_true",
        help="Run the tutorial agent if available",
    )
    parser.add_argument(
        "--from-field",
        dest="from_field",
        default="frederich.torresi@optimumsystems.com",
        help="Sender identifier (used to fill the UserPrompt) when using --run-return-request",
    )
    parser.add_argument(
        "--content",
        dest="content",
        default="My Percision Gear Set with Serial No: 8dc04f7a-ec70-4c79-9eba-759396546948 has jammed, I think some of the cables have frayed.",
        help="Customer message content when using --run-return-request",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the agent run to `logs/` as JSON (+ Markdown summary if available)",
    )
    parser.add_argument(
        "--format",
        choices=["pretty", "json", "md"],
        default="pretty",
        help="Output format when printing agent results to terminal",
    )
    args = parser.parse_args()

    if args.run_agent:
        try:
            # tutorial agent may exist at top-level `agents` package or inside this package
            try:
                from lato_langchain.agents.tutorial_agent import run_agent
            except Exception:
                from agents.tutorial_agent import run_agent
        except Exception as e:
            print("Failed to import or initialize the tutorial agent:", e)
        else:
            print("Running tutorial agent...")
            res = run_agent(args.message)
            try:
                print(json.dumps(res, indent=2, ensure_ascii=False, default=str))
            except Exception:
                print(res)

    if args.run_return_request:
        try:
            from lato_langchain.agents.return_request_agent import run_return_request_agent
            from lato_langchain.utils.print_helpers import rich_print_run, find_repair_summary, save_run
        except Exception as e:
            print("Failed to import or initialize the return request agent:", e)
            return

        print("Running return request agent...")
        try:
            result_obj = run_return_request_agent(args.from_field, args.content)
            raw = result_obj.get("raw")
            summary = result_obj.get("summary")

            if args.format == "json":
                try:
                    print(json.dumps(raw, indent=2, ensure_ascii=False, default=str))
                except Exception:
                    print(raw)
            elif args.format == "md":
                if summary:
                    print(summary)
                else:
                    print("(no summary found)")
            else:  # pretty
                try:
                    rich_print_run(raw)
                except Exception:
                    try:
                        print(json.dumps(raw, indent=2, ensure_ascii=False, default=str))
                    except Exception:
                        print(raw)

            if args.save:
                try:
                    logs_dir = os.path.join(os.getcwd(), "logs")
                    os.makedirs(logs_dir, exist_ok=True)
                    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                    base = os.path.join(logs_dir, f"agent_run_{ts}")
                    json_path = f"{base}.json"
                    save_run(raw, json_path)
                    print(f"Saved run to: {json_path}")
                    if summary:
                        md_path = f"{base}.md"
                        with open(md_path, "w", encoding="utf-8") as fh:
                            fh.write(summary)
                        print(f"Saved summary to: {md_path}")
                except Exception as e:
                    print("Failed to save run:", e)
        except Exception as e:
            print("Error while running return request agent:", e)


if __name__ == "__main__":
    main()
